import json
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.constants.state import IterationStepTemplates


STEP_TO_ITERATION_SLOT_MAPPING = {
    "prepare_mining": "mining_input_dataset_id",
    "mining": "mining_output_dataset_id",
    "label": "label_output_dataset_id",
    "prepare_training": "training_input_dataset_id",
    "training": "training_output_model_id",
}


@dataclass
class IterationStepTemplate:
    name: str
    project: models.Project
    previous_iteration: Optional[models.Iteration]

    presetting: Optional[Dict] = None
    serialized_presetting: Optional[str] = None

    def __post_init__(self) -> None:
        method_name = f"{self.name}_initializer"
        self.presetting = getattr(self, method_name)(self.name, self.project, self.previous_iteration)
        self.serialized_presetting = json.dumps(self.presetting)

    @staticmethod
    def get_step(step_name: str, iteration: Optional[models.Iteration]) -> Optional[models.IterationStep]:
        """
        get corresponding step from previous iteration
        """
        if not iteration:
            return None
        return next(step for step in iteration.iteration_steps if step.name == step_name)

    def get_prior_presetting(
        self, iteration: Optional[models.Iteration], parameter_names: Optional[List[str]] = None
    ) -> Dict:
        prior_step = self.get_step(self.name, iteration)
        if not prior_step:
            return {}
        if parameter_names:
            return {k: v for k, v in prior_step.presetting.items() if k in parameter_names}
        return prior_step.presetting

    def prepare_mining_initializer(
        self, name: str, project: models.Project, previous_iteration: Optional[models.Iteration]
    ) -> Dict:
        presetting: Dict = {"mining_dataset_id": project.mining_dataset_id}
        if not previous_iteration:
            return presetting

        last_training_step = self.get_step("training", previous_iteration)
        if last_training_step and last_training_step.presetting:
            exclude_datasets = [
                last_training_step.presetting.get("dataset_id"),
                last_training_step.presetting.get("validation_dataset_id"),
            ]
            presetting["exclude_datasets"] = [i for i in exclude_datasets if i]

        sticky_parameters = ["mining_strategy", "exclude_last_result", "sampling_count"]
        prior_presetting = self.get_prior_presetting(previous_iteration, sticky_parameters)
        presetting.update(prior_presetting)
        return presetting

    def mining_initializer(
        self, name: str, project: models.Project, previous_iteration: Optional[models.Iteration]
    ) -> Dict:
        if not previous_iteration:
            return {"model_id": project.initial_model_id}
        sticky_parameters = ["top_k", "generate_annotations", "docker_image_id", "docker_image_config"]
        presetting = self.get_prior_presetting(previous_iteration, sticky_parameters)

        last_training_step = self.get_step("training", previous_iteration)
        presetting["model_id"] = last_training_step.result_model.id  # type: ignore
        return presetting

    def label_initializer(self, name: str, project: models.Project, previous_iteration: models.Iteration) -> Dict:
        presetting = {"keywords": project.training_targets}
        if not previous_iteration:
            return presetting
        sticky_parameters = ["annotation_type", "extra_url"]
        prior_presetting = self.get_prior_presetting(previous_iteration, sticky_parameters)
        presetting.update(prior_presetting)
        return presetting

    def prepare_training_initializer(
        self, name: str, project: models.Project, previous_iteration: models.Iteration
    ) -> Dict:
        if not previous_iteration:
            return {"training_dataset_id": project.initial_training_dataset_id}
        last_prepare_training_step = self.get_step("prepare_training", previous_iteration)
        return {"training_dataset_id": last_prepare_training_step.result_dataset.id}  # type: ignore

    def training_initializer(self, name: str, project: models.Project, previous_iteration: models.Iteration) -> Dict:
        presetting = {"validation_dataset_id": project.validation_dataset_id}
        if not previous_iteration:
            return presetting
        sticky_parameters = ["docker_image_id", "docker_image_config", "model_id", "model_stage_id"]
        prior_presetting = self.get_prior_presetting(previous_iteration, sticky_parameters)
        presetting.update(prior_presetting)
        return presetting


def initialize_steps(
    db: Session,
    iteration_id: int,
    project: models.Project,
    previous_iteration: models.Iteration,
) -> List[models.IterationStep]:
    """
    Initialize all the necessary steps upon new iteration with project and iteration context.

    project context:
    - candidate_training_dataset_id

    previous iteration context:
    - task parameters
    """
    steps = [
        schemas.iteration_step.IterationStepCreate(
            iteration_id=iteration_id,
            name=step_template.name,
            task_type=step_template.task_type,
            serialized_presetting=IterationStepTemplate(
                step_template.name, project, previous_iteration
            ).serialized_presetting,
        )
        for step_template in IterationStepTemplates
    ]
    return crud.iteration_step.batch_create(db, objs_in=steps)


def backfill_iteration_slots(db: Session, iteration_id: int, step_name: str, result_id: int) -> None:
    """
    backfill iteration step result to iteration table for compatibility
    """
    updates = {STEP_TO_ITERATION_SLOT_MAPPING[step_name]: result_id}
    crud.iteration.update_iteration(db, iteration_id=iteration_id, iteration_update=schemas.IterationUpdate(**updates))
