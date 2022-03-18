
type Dataset = number
export interface Project {
  id: number,
  name: string,
  type: number,
  keywords: Array<string>,
  targetMap: number,
  targetDataset: number,
  targetIteration: number,
  trainSet: Dataset,
  testSet: Dataset,
  miningSet: Dataset,
  setCount: number,
  modelCount: number,
  miningStrategy: number,
  chunkSize?: number,
  currentIteration?: number,
  createTime: string,
  updateTime: string,
  description?: string,
}

export interface Iteration {
  id: number,
  name: string,
  version: number,
  currentStep: number,
  trainSet?: Dataset,
  trainUpdateSet: Dataset,
  miningSet?: Dataset,
  miningResult?: Dataset,
  labelSet?: Dataset,
  model?: number,
}
export interface originIteration {
  id: number,
  name: string,
  version: number,
  current_step: number,
  train_set: Dataset,
  train_update_result: Dataset,
  mining_set?: Dataset,
  mining_result?: Dataset,
  label_set?: Dataset,
  model?: number,
}

export interface originProject {
  id: number,
  name: string,
  training_keywords: Array<string>,
  train_set: Dataset,
  test_set: Dataset,
  mining_set: Dataset,
  dataset_count: number,
  model_count: number,
  mining_strategy: number,
  chunk_size: number,
  current_iteration?: originIteration,
  create_datetime: string,
  update_datetime: string,
  description: string 
  training_type: number,
  iteration_target: number,
  map_target: number,
  training_dataset_count_target: number,
  current_iteration_id: number,
}
