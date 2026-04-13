# app/api/v1/fundraising.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.api.deps import get_current_user, require_role
from app.models.user import User, UserRole
from app.models.fundraising import Fundraising, Donation, FundraisingExpense
from app.models.problem import Problem
from app.schemas.fundraising import (
    FundraisingCreate,
    FundraisingPublic,
    DonationCreate,
    DonationPublic,
    DonationsList,
    ExpenseCreate,
    ExpensePublic,
    ExpensesList,
)
from app.services.versioning import create_new_version

router = APIRouter(prefix="/fundraising", tags=["fundraising"])


@router.post("/problems/{problem_id}/fundraising", response_model=FundraisingPublic)
def create_fundraising(
    problem_id: int,
    data: FundraisingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin])),
):
    """Создать сбор средств для проблемы (только модераторы)"""
    # Проверяем существование проблемы
    problem = db.query(Problem).filter(
        Problem.entity_id == problem_id,
        Problem.is_current
    ).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проблема не найдена"
        )

    # Проверяем, нет ли уже активного сбора
    existing = db.query(Fundraising).filter(
        Fundraising.problem_entity_id == problem_id,
        Fundraising.is_current,
        Fundraising.status == "active"
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Для этой проблемы уже есть активный сбор средств"
        )

    # Создаем сбор
    entity_id = Fundraising.next_entity_id(db)
    fundraising = Fundraising(
        entity_id=entity_id,
        version=1,
        is_current=True,
        changed_by_id=current_user.entity_id,
        problem_entity_id=problem_id,
        goal_amount=data.goal_amount,
        current_amount=0.0,
        currency=data.currency,
        deadline=data.deadline,
        status="active",
        description=data.description,
    )

    db.add(fundraising)
    db.commit()
    db.refresh(fundraising)

    return fundraising


@router.get("/problems/{problem_id}/fundraising", response_model=FundraisingPublic)
def get_problem_fundraising(
    problem_id: int,
    db: Session = Depends(get_db),
):
    """Получить информацию о сборе средств для проблемы"""
    fundraising = db.query(Fundraising).filter(
        Fundraising.problem_entity_id == problem_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    return fundraising


@router.post("/{fundraising_id}/donate", response_model=DonationPublic)
def make_donation(
    fundraising_id: int,
    data: DonationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Сделать пожертвование"""
    # Проверяем существование сбора
    fundraising = db.query(Fundraising).filter(
        Fundraising.entity_id == fundraising_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    if fundraising.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сбор средств неактивен"
        )

    # Создаем пожертвование
    entity_id = Donation.next_entity_id(db)
    donation = Donation(
        entity_id=entity_id,
        version=1,
        is_current=True,
        changed_by_id=current_user.entity_id,
        fundraising_entity_id=fundraising_id,
        donor_entity_id=None if data.is_anonymous else current_user.entity_id,
        amount=data.amount,
        currency=data.currency,
        is_anonymous=data.is_anonymous,
        message=data.message,
    )

    db.add(donation)

    # Обновляем текущую сумму в сборе
    new_current_amount = fundraising.current_amount + data.amount
    new_status = fundraising.status

    # Автоматически завершаем, если достигли цели
    if new_current_amount >= fundraising.goal_amount:
        new_status = "completed"

    create_new_version(
        db=db,
        model_class=Fundraising,
        entity_id=fundraising_id,
        changed_by_id=current_user.entity_id,
        change_reason=f"Donation {entity_id}",
        current_amount=new_current_amount,
        status=new_status,
    )

    db.commit()
    db.refresh(donation)

    return donation


@router.get("/{fundraising_id}/donations", response_model=DonationsList)
def get_donations(
    fundraising_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Получить список пожертвований"""
    # Проверяем существование сбора
    fundraising = db.query(Fundraising).filter(
        Fundraising.entity_id == fundraising_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    # Получаем пожертвования
    donations = db.query(Donation).filter(
        Donation.fundraising_entity_id == fundraising_id,
        Donation.is_current
    ).order_by(Donation.created_at.desc()).offset(skip).limit(limit).all()

    total = db.query(func.count(Donation.entity_id)).filter(
        Donation.fundraising_entity_id == fundraising_id,
        Donation.is_current
    ).scalar()

    total_amount = db.query(func.sum(Donation.amount)).filter(
        Donation.fundraising_entity_id == fundraising_id,
        Donation.is_current
    ).scalar() or 0.0

    return DonationsList(
        items=donations,
        total=total,
        total_amount=total_amount,
    )


@router.post("/{fundraising_id}/expenses", response_model=ExpensePublic)
def add_expense(
    fundraising_id: int,
    data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin])),
):
    """Добавить расход (только модераторы)"""
    # Проверяем существование сбора
    fundraising = db.query(Fundraising).filter(
        Fundraising.entity_id == fundraising_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    # Создаем расход
    entity_id = FundraisingExpense.next_entity_id(db)
    expense = FundraisingExpense(
        entity_id=entity_id,
        version=1,
        is_current=True,
        changed_by_id=current_user.entity_id,
        fundraising_entity_id=fundraising_id,
        amount=data.amount,
        currency=data.currency,
        description=data.description,
        receipt_url=data.receipt_url,
        approved_by_entity_id=current_user.entity_id,
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@router.get("/{fundraising_id}/expenses", response_model=ExpensesList)
def get_expenses(
    fundraising_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Получить список расходов"""
    # Проверяем существование сбора
    fundraising = db.query(Fundraising).filter(
        Fundraising.entity_id == fundraising_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    # Получаем расходы
    expenses = db.query(FundraisingExpense).filter(
        FundraisingExpense.fundraising_entity_id == fundraising_id,
        FundraisingExpense.is_current
    ).order_by(FundraisingExpense.created_at.desc()).offset(skip).limit(limit).all()

    total = db.query(func.count(FundraisingExpense.entity_id)).filter(
        FundraisingExpense.fundraising_entity_id == fundraising_id,
        FundraisingExpense.is_current
    ).scalar()

    total_spent = db.query(func.sum(FundraisingExpense.amount)).filter(
        FundraisingExpense.fundraising_entity_id == fundraising_id,
        FundraisingExpense.is_current
    ).scalar() or 0.0

    return ExpensesList(
        items=expenses,
        total=total,
        total_spent=total_spent,
    )


@router.patch("/{fundraising_id}/status")
def update_fundraising_status(
    fundraising_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.moderator, UserRole.admin])),
):
    """Обновить статус сбора (только модераторы)"""
    if status not in ["active", "completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недопустимый статус"
        )

    fundraising = db.query(Fundraising).filter(
        Fundraising.entity_id == fundraising_id,
        Fundraising.is_current
    ).first()

    if not fundraising:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сбор средств не найден"
        )

    create_new_version(
        db=db,
        model_class=Fundraising,
        entity_id=fundraising_id,
        changed_by_id=current_user.entity_id,
        change_reason=f"Status changed to {status}",
        status=status,
    )

    db.commit()

    return {"message": "Статус обновлен", "status": status}
