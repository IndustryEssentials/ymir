type DatasetId = number

export interface Iteration {
  id: number,
  projectId: number,
  name?: string,
  round: number,
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
