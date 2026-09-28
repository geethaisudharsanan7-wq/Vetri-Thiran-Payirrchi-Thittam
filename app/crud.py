from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Plan
from .database import User
from app.schemas import UserInput


def save_user(
    db: Session,
    data: UserInput,
) -> User:
    """
    Create a new user or update an existing profile.
    """

    user = db.scalar(
        select(User).where(
            User.user_id == data.user_id
        )
    )

    if user:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity

    else:
        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user_id: str,
    workout_plan: str,
    nutrition_tip: str,
) -> Plan:
    """
    Save a newly generated plan.
    """

    plan = Plan(
        user_id=user_id,
        original_plan=workout_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def get_latest_plan(
    db: Session,
    user_id: str,
) -> Plan | None:

    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
    )


def update_plan(
    db: Session,
    plan: Plan,
    updated_plan: str,
    feedback: str,
) -> Plan:

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str,
) -> User | None:

    return db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )


def get_all_users(
    db: Session,
) -> list[User]:

    return list(
        db.scalars(
            select(User)
            .order_by(User.created_at.desc())
        ).all()
    )


def get_all_plans(
    db: Session,
) -> list[Plan]:

    return list(
        db.scalars(
            select(Plan)
            .order_by(Plan.created_at.desc())
        ).all()
    )