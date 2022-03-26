import { Project, originProject, originInteration, Interation, } from "@/interface/project"
import { backendData } from "@/interface/common"
import { transferDatasetGroup, transferDataset } from '@/constants/dataset'
import { format } from '@/utils/date'

export enum Steps {
  beforeMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  trained = 5,
}

export function getInterationVersion (version: number) {
  return `V${version}`
}

export function transferProject(data: backendData) {
  const project : Project = {
    id: data.id,
    name: data.name,
    keywords: data.training_keywords,
    trainSet: data.training_dataset_group ? transferDatasetGroup(data.training_dataset_group) : undefined,
    testSet: data.testing_dataset ? transferDataset(data.testing_dataset) : undefined,
    miningSet: data.mining_dataset ? transferDataset(data.mining_dataset) : undefined,
    setCount: data.dataset_count,
    modelCount: data.model_count,
    miningStrategy: data.mining_strategy,
    chunkSize: data.chunk_size,
    currentInteration: data.current_iteration ? transferInteration(data.current_iteration) : undefined,
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.training_type,
    targetMap: data.map_target,
    targetDataset: data.training_dataset_count_target,
    targetInteration: data.iteration_target,
    updateTime: data.update_datetime,
  }
  return project
}

export function transferInteration (data: originInteration | undefined) {
  if (!data) {
    return
  }
  const interation : Interation = {
    id: data.id,
    name: data.name,
    version: data.version,
    currentStep: data.current_step,
    currentStage: data.current_stage,
    iterationRound: data.iteration_round,
    trainSet: data.train_set,
    trainUpdateSet: data.train_update_result,
    miningResult: data.mining_result,
    labelSet: data.label_set,
    miningSet: data.mining_set,
    model: data.model,
    
  }
  return interation
}
