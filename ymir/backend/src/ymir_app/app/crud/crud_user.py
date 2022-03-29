from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserRole, UserState, UserUpdate
from app.utils.security import get_password_hash, verify_password
from app.config import settings


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        state = UserState.registered.value if settings.REGISTRATION_NEEDS_APPROVAL else UserState.active.value
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            state=state,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def get_multi_with_filter(
        self,
        db: Session,
        *,
        offset: Optional[int] = 0,
        limit: Optional[int] = None,
        **filters: Any,
    ) -> Tuple[List[User], int]:
        query = db.query(self.model)
        if filters.get("state"):
            query = query.filter(User.state == int(filters["state"]))
        query = query.order_by(desc(self.model.create_datetime))
        if limit:
            return query.offset(offset).limit(limit).all(), query.count()
        else:
            return query.all(), query.count()

    def update_state(self, db: Session, *, user: User, state: UserState) -> User:
        update_data = {"state": int(state)}
        return self.update(db, db_obj=user, obj_in=update_data)

    def update_role(self, db: Session, *, user: User, role: UserRole) -> User:
        update_data = {"role": int(role)}
        return self.update(db, db_obj=user, obj_in=update_data)

    def update_login_time(self, db: Session, *, user: User) -> User:
        update_data = {"last_login_datetime": datetime.utcnow()}
        return self.update(db, db_obj=user, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def activate(self, db: Session, *, user: User) -> User:
        return self.update_state(db, user=user, state=UserState.active)

    def deactivate(self, db: Session, *, user: User) -> User:
        return self.update_state(db, user=user, state=UserState.deactivated)

    def is_deleted(self, user: User) -> bool:
        return user.is_deleted

    def is_active(self, user: User) -> bool:
        return user.state == UserState.active


user = CRUDUser(User)
