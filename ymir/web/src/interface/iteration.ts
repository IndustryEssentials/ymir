type DatasetId = number

export interface Iteration {
  id: number,
  projectId: number,
  name?: string,
  round: number,
  currentStep: Step,
  steps: Step[],
  currentStage: number,
  testSet?: DatasetId,
  trainSet?: DatasetId,
  trainUpdateSet: DatasetId,
  wholeMiningSet: DatasetId,
  miningSet?: DatasetId,
  miningResult?: DatasetId,
  labelSet?: DatasetId,
  model?: number,
  prevIteration: number,
}

export interface Step {
  id: number,
  finished: boolean,
  name: string,
  percent: number,
  presetting: any,
  state: number,
  taskId: number,
  taskType: number,
}
