from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .models import User, WorkoutPlan
from .schemas import UserInput


def save_user(
    db: Session,
    data: UserInput,
) -> User:

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
            **data.model_dump()
        )

        db.add(user)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    original_plan: str,
    nutrition_tip: str,
) -> WorkoutPlan:

    plan = WorkoutPlan(
        user_id=user.id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def get_user(
    db: Session,
    user_id: str,
) -> User | None:

    return db.scalar(
        select(User)
        .options(
            joinedload(User.plans)
        )
        .where(
            User.user_id == user_id
        )
    )


def get_latest_plan(
    db: Session,
    user: User,
) -> WorkoutPlan | None:

    return db.scalar(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user.id
        )
        .order_by(
            WorkoutPlan.created_at.desc()
        )
        .limit(1)
    )


def get_original_plan(
    db: Session,
    user_id: str,
) -> WorkoutPlan | None:

    user = get_user(
        db,
        user_id,
    )

    if not user:
        return None

    return get_latest_plan(
        db,
        user,
    )


def update_plan(
    db: Session,
    plan: WorkoutPlan,
    revised_plan: str,
    feedback: str,
    nutrition_tip: str,
) -> WorkoutPlan:

    plan.updated_plan = revised_plan

    plan.feedback = feedback

    plan.updated_nutrition_tip = nutrition_tip

    db.commit()

    db.refresh(plan)

    return plan


def get_all_users(
    db: Session,
) -> list[User]:

    users = list(
        db.scalars(
            select(User)
            .options(
                joinedload(User.plans)
            )
            .order_by(
                User.created_at.desc()
            )
        )
        .unique()
        .all()
    )

    return users


def delete_user(
    db: Session,
    user_id: str,
) -> bool:

    user = db.scalar(
        select(User).where(
            User.user_id == user_id
        )
    )

    if not user:
        return False

    db.delete(user)

    db.commit()

    return True