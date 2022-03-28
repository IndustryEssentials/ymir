import { DatasetGroup, Dataset } from "@/interface/dataset"
type DatasetId = number
export interface Project {
  id: number,
  name: string,
  type: number,
  keywords: Array<string>,
  targetMap: number,
  targetDataset: number,
  targetIteration: number,
  trainSet?: DatasetGroup,
  testSet?: Dataset,
  miningSet?: Dataset,
  setCount: number,
  modelCount: number,
  miningStrategy: number,
  chunkSize?: number,
  currentIteration?: Iteration,
  createTime: string,
  updateTime: string,
  description?: string,
}

export interface Iteration {
  id: number,
  name?: string,
  round: number,
  currentStage: number,
  trainSet?: DatasetId,
  trainUpdateSet: DatasetId,
  miningSet?: DatasetId,
  miningResult?: DatasetId,
  labelSet?: DatasetId,
  model?: number,
}
