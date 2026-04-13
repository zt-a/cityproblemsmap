# app/api/v1/analytics_extended.py
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import io
import csv
from datetime import datetime, timezone
from geoalchemy2.shape import to_shape

from app.database import get_db
from app.api.deps import get_current_user
from app.schemas.analytics_extended import (
    ZoneComparison,
    TopZone,
    UserLeaderboard,
    OfficialEfficiency,
    ProblemTrend,
)
from app.services.analytics_extended import (
    get_zones_comparison,
    get_top_problematic_zones,
    get_user_leaderboard,
    get_officials_efficiency,
    get_problem_trends_by_type,
)
from app.models.problem import Problem
from app.models.zone import Zone
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics-extended"])


@router.get("/zones/comparison", response_model=list[ZoneComparison])
def compare_zones(
    zone_ids: str = Query(..., description="Comma-separated zone IDs"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Сравнение нескольких зон"""
    try:
        ids = [int(id.strip()) for id in zone_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid zone IDs format")

    if len(ids) < 2:
        raise HTTPException(
            status_code=400, detail="At least 2 zones required for comparison"
        )

    if len(ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 zones for comparison")

    return get_zones_comparison(db, ids)


@router.get("/zones/top", response_model=list[TopZone])
def top_problematic_zones(
    city: str,
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Топ проблемных зон города"""
    return get_top_problematic_zones(db, city, limit)


@router.get("/leaderboard/users", response_model=list[UserLeaderboard])
def user_leaderboard(
    city: str,
    limit: int = Query(50, ge=1, le=100),
    period_days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Рейтинг активных пользователей"""
    return get_user_leaderboard(db, city, limit, period_days)


@router.get("/leaderboard/officials", response_model=list[OfficialEfficiency])
def officials_efficiency(
    city: str,
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Рейтинг эффективности официальных лиц"""
    return get_officials_efficiency(db, city, limit)


@router.get("/trends/by-type", response_model=list[ProblemTrend])
def problem_trends_by_type(
    city: str,
    days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
):
    """Тренды по типам проблем"""
    return get_problem_trends_by_type(db, city, days)


@router.get("/export/problems")
def export_problems(
    city: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Экспорт данных о проблемах"""
    query = db.query(Problem).filter(
        Problem.city == city,
        Problem.is_current,
    )

    if status:
        query = query.filter(Problem.status == status)

    problems = query.all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Заголовки
        writer.writerow([
            "ID",
            "Title",
            "Description",
            "Status",
            "Type",
            "Priority",
            "Created At",
            "Author ID",
            "Zone ID",
            "Latitude",
            "Longitude",
        ])

        # Данные
        for problem in problems:
            point = to_shape(problem.location)
            writer.writerow([
                problem.entity_id,
                problem.title,
                problem.description[:100] if problem.description else "",
                problem.status.value,
                problem.problem_type.value,
                problem.priority_score,
                problem.created_at.isoformat(),
                problem.author_entity_id,
                problem.zone_entity_id,
                point.y,
                point.x,
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=problems_{city}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
            },
        )

    elif format == "json":
        data = []
        for p in problems:
            point = to_shape(p.location)
            data.append({
                "id": p.entity_id,
                "title": p.title,
                "description": p.description,
                "status": p.status.value,
                "type": p.problem_type.value,
                "priority": p.priority_score,
                "created_at": p.created_at.isoformat(),
                "author_id": p.author_entity_id,
                "zone_id": p.zone_entity_id,
                "latitude": point.y,
                "longitude": point.x,
            })
        return data


@router.get("/export/zones")
def export_zones(
    city: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    """Экспорт данных о зонах"""
    zones = db.query(Zone).filter(
        Zone.city == city,
        Zone.is_current,
    ).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Name",
            "Type",
            "Total Problems",
            "Open Problems",
            "Solved Problems",
            "Risk Score",
            "Pollution Index",
            "Traffic Index",
            "Center Lat",
            "Center Lon",
        ])

        for zone in zones:
            writer.writerow([
                zone.entity_id,
                zone.name,
                zone.zone_type,
                zone.total_problems,
                zone.open_problems,
                zone.solved_problems,
                zone.risk_score,
                zone.pollution_index,
                zone.traffic_index,
                zone.center_lat,
                zone.center_lon,
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=zones_{city}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
            },
        )

    elif format == "json":
        data = [
            {
                "id": z.entity_id,
                "name": z.name,
                "type": z.zone_type,
                "total_problems": z.total_problems,
                "open_problems": z.open_problems,
                "solved_problems": z.solved_problems,
                "risk_score": z.risk_score,
                "pollution_index": z.pollution_index,
                "traffic_index": z.traffic_index,
                "center_lat": z.center_lat,
                "center_lon": z.center_lon,
            }
            for z in zones
        ]
        return data


@router.get("/export/users")
def export_users(
    city: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db),
):
    """Экспорт данных о пользователях"""
    users = db.query(User).filter(
        User.city == city,
        User.is_current,
    ).all()

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "ID",
            "Username",
            "Email",
            "Role",
            "Status",
            "Reputation",
            "City",
            "District",
            "Created At",
        ])

        for user in users:
            writer.writerow([
                user.entity_id,
                user.username,
                user.email,
                user.role.value,
                user.status.value,
                user.reputation,
                user.city,
                user.district,
                user.created_at.isoformat(),
            ])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=users_{city}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
            },
        )

    elif format == "json":
        data = [
            {
                "id": u.entity_id,
                "username": u.username,
                "email": u.email,
                "role": u.role.value,
                "status": u.status.value,
                "reputation": u.reputation,
                "city": u.city,
                "district": u.district,
                "created_at": u.created_at.isoformat(),
            }
            for u in users
        ]
        return data
