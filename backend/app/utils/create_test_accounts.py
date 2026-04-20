# app/utils/create_test_accounts.py
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.services.auth import hash_password, get_user_by_email
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def create_test_account(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: UserRole,
    city: str = "Bishkek"
) -> User | None:
    """
    Create a test account if it doesn't exist.
    Returns the user if created or already exists, None if credentials are missing.
    """
    # Skip if any required field is empty
    if not username or not email or not password:
        logger.info(f"Skipping {role.value} account creation - missing credentials")
        return None

    # Check if user already exists
    existing_user = get_user_by_email(db, email)
    if existing_user:
        logger.info(f"Test account {email} already exists, skipping creation")
        return existing_user

    # Create new user
    try:
        entity_id = User.next_entity_id(db)
        user = User(
            entity_id=entity_id,
            version=1,
            is_current=True,
            username=username,
            email=email,
            hashed_password=hash_password(password),
            role=role,
            city=city,
            country="Kyrgyzstan",
            reputation=100.0,  # Give test accounts some reputation
            is_verified=True,  # Mark as verified
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"✅ Created test account: {username} ({email}) with role {role.value}")
        return user
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create test account {email}: {e}")
        return None


def create_all_test_accounts(db: Session):
    """
    Create all test accounts based on environment variables.
    Only runs if CREATE_TEST_ACCOUNTS=true in .env
    """
    if not settings.CREATE_TEST_ACCOUNTS:
        logger.info("Test account creation disabled (CREATE_TEST_ACCOUNTS=false)")
        return

    logger.info("🔧 Creating test accounts...")

    # Admin account
    create_test_account(
        db,
        username=settings.TEST_ADMIN_USERNAME,
        email=settings.TEST_ADMIN_EMAIL,
        password=settings.TEST_ADMIN_PASSWORD,
        role=UserRole.admin,
    )

    # Moderator account
    create_test_account(
        db,
        username=settings.TEST_MODERATOR_USERNAME,
        email=settings.TEST_MODERATOR_EMAIL,
        password=settings.TEST_MODERATOR_PASSWORD,
        role=UserRole.moderator,
    )

    # Official account
    create_test_account(
        db,
        username=settings.TEST_OFFICIAL_USERNAME,
        email=settings.TEST_OFFICIAL_EMAIL,
        password=settings.TEST_OFFICIAL_PASSWORD,
        role=UserRole.official,
    )

    # Volunteer account
    create_test_account(
        db,
        username=settings.TEST_VOLUNTEER_USERNAME,
        email=settings.TEST_VOLUNTEER_EMAIL,
        password=settings.TEST_VOLUNTEER_PASSWORD,
        role=UserRole.volunteer,
    )

    # Regular user account
    create_test_account(
        db,
        username=settings.TEST_USER_USERNAME,
        email=settings.TEST_USER_EMAIL,
        password=settings.TEST_USER_PASSWORD,
        role=UserRole.user,
    )

    logger.info("✅ Test account creation completed")
