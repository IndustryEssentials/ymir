from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import not_
from sqlalchemy.orm import Session

from app.config import settings
from app.constants.state import ResultState
from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()  # type: ignore

    def get_by_user_and_id(self, db: Session, *, user_id: int, id: Any) -> Optional[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.id == id,  # type: ignore
                self.model.user_id == user_id,  # type: ignore
                not_(self.model.is_deleted),  # type: ignore
            )
            .first()
        )

    def get_by_name(self, db: Session, name: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.name == name).first()  # type: ignore

    def get_by_user_and_name(self, db: Session, user_id: int, name: str) -> Optional[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,  # type: ignore
                self.model.name == name,  # type: ignore
                not_(self.model.is_deleted),  # type: ignore
            )
            .one_or_none()
        )

    def get_by_hash(self, db: Session, hash_: str) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.hash == hash_).first()  # type: ignore

    def get_by_task_id(self, db: Session, task_id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.task_id == task_id).first()  # type: ignore

    def get_multi(self, db: Session, *, offset: int = 0, limit: int = settings.DEFAULT_LIMIT) -> List[ModelType]:
        return db.query(self.model).offset(offset).limit(limit).all()

    def get_multi_by_ids(self, db: Session, *, ids: List[int]) -> List[ModelType]:
        if len(ids) == 0:
            return []
        return db.query(self.model).filter(self.model.id.in_(ids)).all()  # type: ignore

    def get_multi_by_user(self, db: Session, *, user_id: int) -> List[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,  # type: ignore
                not_(self.model.is_deleted),  # type: ignore
            )
            .all()
        )

    def get_multi_by_project(self, db: Session, *, project_id: int) -> List[ModelType]:
        return (
            db.query(self.model)
            .filter(
                self.model.project_id == project_id,  # type: ignore
            )
            .all()
        )

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def create_with_user_id(self, db: Session, *, user_id: int, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        obj_in_data["user_id"] = user_id
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj

    def soft_remove(self, db: Session, *, id: int) -> Optional[ModelType]:
        obj = db.query(self.model).get(id)
        if not obj:
            return None
        obj.is_deleted = True  # type: ignore
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def set_result_state_to_error(self, db: Session, id: int) -> None:
        obj = db.query(self.model).get(id)
        if not obj:
            return None
        obj.result_state = int(ResultState.error)  # type: ignore
        db.add(obj)
        db.commit()
        db.refresh(obj)

    def total(self, db: Session) -> int:
        return db.query(self.model).count()

    def is_duplicated_name(self, db: Session, user_id: int, name: str) -> bool:
        return self.get_by_user_and_name(db, user_id, name) is not None

    def is_duplicated_name_in_project(self, db: Session, project_id: int, name: str) -> bool:
        existing = (
            db.query(self.model)
            .filter(
                self.model.project_id == project_id,  # type: ignore
                self.model.name == name,  # type: ignore
                not_(self.model.is_deleted),  # type: ignore
            )
            .one_or_none()
        )
        return existing is not None

    def is_duplicated_hash(self, db: Session, project_id: int, hash_: str) -> bool:
        existing = (
            db.query(self.model)
            .filter(
                self.model.project_id == project_id,  # type: ignore
                self.model.hash == hash_,  # type: ignore
                not_(self.model.is_deleted),  # type: ignore
            )
            .one_or_none()
        )
        return existing is not None
