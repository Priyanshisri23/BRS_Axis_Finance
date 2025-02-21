import sys
sys.path.append('.')
# from app.db.session import SessionLocal
from app.db.db_engine import get_session, SessionLocal 
from app.models.user import User
from app.models.log import Log  # Ensure this is imported
from app.core.security import get_password_hash

def create_superuser():
    """Create a superuser in the system."""
    db = SessionLocal
    print(f"DB: {db}")
    try:
        # Define superuser details
        username = "rahul"
        email = "BRS.AutoMail@axisfinance.in"
        password = "rahul"

        # Check if the user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            print(f"Superuser with username '{username}' or email '{email}' already exists.")
            return

        # Create the superuser
        superuser = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            first_name="Rahul",
            last_name="Raj",
            is_active=True,
            is_superuser=True
        )
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        print(f"Superuser '{username}' created successfully.")
    except Exception as e:
        db.rollback()
        print(f"Error creating superuser: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_superuser()
