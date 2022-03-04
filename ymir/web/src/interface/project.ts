
type Dataset = number
export interface Project {
  id: number,
  name: string,
  type: number,
  keywords: Array<string>,
  targetMap: number,
  targetDataset: number,
  targetInteration: number,
  trainSet: Dataset,
  testSet: Dataset,
  miningSet: Dataset,
  setsAccount: number,
  modelsAccount: number,
  miningStrategy: number,
  chunkSize?: number,
  currentInteration?: Interation,
  createTime: string,
  description?: string,
}

export interface Interation {
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
export interface originInteration {
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
  set_account: number,
  models_account: number,
  mining_strategy: number,
  chunk_size?: number,
  current_interation?: originInteration,
  create_datetime: string,
  description?: string 
  training_type: number,
  iteration_target: number,
  map_target: number,
  training_dataset_count_target: number,
}
