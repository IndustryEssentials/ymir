import { Project, originProject, originInteration, Interation, } from "@/interface/project"
import { format } from '@/utils/date'

export enum Steps {
  beforeMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  trained = 5,
}

/**
 * get interation version name
 * @param version interation version
 * @returns 
 */
export function getInterationVersion (version: number) {
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
    setsAccount: data.set_account,
    modelsAccount: data.models_account,
    miningStrategy: data.mining_strategy,
    chunkSize: data.chunk_size,
    currentInteration: transferInteration(data.current_interation),
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.training_type,
    targetMap: data.map_target,
    targetDataset: data.training_dataset_count_target,
    targetInteration: data.iteration_target,
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
    trainSet: data.train_set,
    trainUpdateSet: data.train_update_result,
    miningResult: data.mining_result,
    labelSet: data.label_set,
    miningSet: data.mining_set,
    model: data.model,
    
  }
  return interation
}
