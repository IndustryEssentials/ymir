from typing import Any


class IterationFSM:
    def __init__(self) -> None:
        self.new_stage(PrepareMiningStage)

    def new_stage(self, newstage: Any) -> None:
        self._stage = newstage


class IterationStage:
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        raise NotImplementedError()

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        raise NotImplementedError()


class PrepareMiningStage(IterationStage):
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        # set mining_input
        ...

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        iteration.new_stage(MiningStage)


class MiningStage(IterationStage):
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        # set mining_output
        ...

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        iteration.new_stage(LabelStage)


class LabelStage(IterationStage):
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        # set label_output
        ...

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        iteration.new_stage(PrepareTrainingStage)


class PrepareTrainingStage(IterationStage):
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        # set training_input
        ...

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        iteration.new_stage(TrainingStage)


class TrainingStage(IterationStage):
    @staticmethod
    def set_iteration_context(iteration: IterationFSM, data: Any) -> None:
        # set training_output
        ...

    @staticmethod
    def next_stage(iteration: IterationFSM) -> None:
        # training stage is the last stage
        return
