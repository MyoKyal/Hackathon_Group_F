"""One-off: promote an existing user to admin by email.

Usage: python scripts/promote_admin.py user@example.com
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from app.db import SessionLocal
from app.models.user import User


def promote(email: str) -> None:
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            print(f"No user found with email {email}")
            return
        user.is_admin = True
        db.commit()
        print(f"{email} is now an admin.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/promote_admin.py user@example.com")
        sys.exit(1)
    promote(sys.argv[1])
