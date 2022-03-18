import { Project, originProject, originIteration, Iteration, } from "@/interface/project"
import { format } from '@/utils/date'

export enum Steps {
  beforeMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  trained = 5,
}

export function getIterationVersion (version: number) {
  return `V${version}`
}

export function transferProject(data: originProject) {
  const project : Project = {
    id: data.id,
    name: data.name,
    keywords: data.training_keywords,
    trainSet: data.train_set,
    testSet: data.test_set,
    miningSet: data.mining_set,
    setCount: data.dataset_count,
    modelCount: data.model_count,
    miningStrategy: data.mining_strategy,
    chunkSize: data.chunk_size,
    currentIteration: data.current_iteration_id,
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.training_type,
    targetMap: data.map_target,
    targetDataset: data.training_dataset_count_target,
    targetIteration: data.iteration_target,
    updateTime: data.update_datetime,
  }
  return project
}

export function transferIteration (data: originIteration | undefined) {
  if (!data) {
    return
  }
  const iteration : Iteration = {
    id: data.id,
    name: data.name,
    version: data.version,
    currentStep: data.current_step,
    trainSet: data.train_set,
    trainUpdateSet: data.train_update_result,
    miningResult: data.mining_result,
    labelSet: data.label_set,
    miningSet: data.mining_set,
    model: data.model,
    
  }
  return iteration
}
