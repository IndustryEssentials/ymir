
type Dataset = number
export interface Project {
  id: number,
  name: string,
  keywords: Array<string>,
  trainSet: Dataset,
  testSet: Dataset,
  miningSet: Dataset,
  setsAccount: number,
  modelsAccount: number,
  ambition?: {
    type: string,
    value: number,
  },
  miningStrategy: number,
  miningBlock?: number,
  currentInteration?: number,
  createTime: string,
  desc?: string,
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
  keywords: Array<string>,
  train_set: Dataset,
  test_set: Dataset,
  mining_set: Dataset,

  set_account: number,
  models_account: number,
  flag?: {
    type: string,
    value: number
  },

  mining_strategy: number,
  current_interation?: number,
  create_datetime: string,
  description?: string 
}