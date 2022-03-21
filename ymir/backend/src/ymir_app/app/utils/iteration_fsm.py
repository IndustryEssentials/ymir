from __future__ import annotations
from typing import Type
from sqlalchemy.orm import Session

from app import crud, schemas
from app.constants.state import IterationStage


class IterationFSM:
    def __init__(self, db: Session, iteration_id: int, stage: IterationStage = IterationStage.prepare_mining) -> None:
        self.db = db
        self.id_ = iteration_id
        self.new_stage(self._fsm_stage(stage))

    def new_stage(self, newstage: Type[FSMStage]) -> None:
        self._stage = newstage

    def verify_stage(self, next_stage: IterationStage) -> bool:
        return self._stage.verify_stage(self, self._fsm_stage(next_stage))

    def proceed(self, result_id: int) -> None:
        return self._stage.proceed(self, result_id)

    def save(self, updates: schemas.IterationUpdate) -> None:
        crud.iteration.proceed_to_next_stage(self.db, iteration_id=self.id_, iteration_update=updates)

    @staticmethod
    def _fsm_stage(stage: IterationStage) -> Type[FSMStage]:
        return STAGE_MAPPING[stage]


class IterationStopError(Exception):
    pass


class FSMStage:
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        raise NotImplementedError()

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        raise NotImplementedError()


class PrepareMiningStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        return DesiredStage is MiningStage

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        update_ = schemas.IterationUpdate(current_stage=IterationStage.mining, mining_input_dataset_id=result_id)
        iteration.save(update_)


class MiningStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        return DesiredStage is LabelStage

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        update_ = schemas.IterationUpdate(current_stage=IterationStage.label, mining_output_dataset_id=result_id)
        iteration.save(update_)


class LabelStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        return DesiredStage is PrepareTrainingStage

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        update_ = schemas.IterationUpdate(
            current_stage=IterationStage.prepare_training, label_output_dataset_id=result_id
        )
        iteration.save(update_)


class PrepareTrainingStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        return DesiredStage is TrainingStage

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        update_ = schemas.IterationUpdate(current_stage=IterationStage.training, training_input_dataset_id=result_id)
        iteration.save(update_)


class TrainingStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        return DesiredStage is EndStage

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        update_ = schemas.IterationUpdate(current_stage=IterationStage.training, training_output_model_id=result_id)
        iteration.save(update_)


class EndStage(FSMStage):
    @staticmethod
    def verify_stage(iteration: IterationFSM, DesiredStage: Type[FSMStage]) -> bool:
        # iteration has reached final stage, refuse to update
        return False

    @staticmethod
    def proceed(iteration: IterationFSM, result_id: int) -> None:
        raise IterationStopError()


STAGE_MAPPING = {
    IterationStage.prepare_mining: PrepareMiningStage,
    IterationStage.mining: MiningStage,
    IterationStage.label: LabelStage,
    IterationStage.prepare_training: PrepareTrainingStage,
    IterationStage.training: TrainingStage,
    IterationStage.end: EndStage,
}
