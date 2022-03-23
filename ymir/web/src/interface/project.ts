
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
  name?: string,
  round: number,
  current: number,
  trainSet?: Dataset,
  trainUpdateSet: Dataset,
  miningSet?: Dataset,
  miningResult?: Dataset,
  labelSet?: Dataset,
  model?: number,
}
export interface originIteration {
  id: number,
  name?: string,
  iteration_round?: number,
  current_stage?: number,
  mining_input_dataset_id?: Dataset,
  mining_output_dataset_id?: Dataset,
  label_output_dataset_id?: Dataset,
  training_input_dataset_id?: Dataset,
  training_output_model_id?: Dataset,
  previous_training_dataset_id?: number,
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
