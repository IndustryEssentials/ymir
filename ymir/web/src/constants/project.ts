import { Project, originProject, originInteration, Interation } from "@/interface/project"

enum flag {
  map = 'mAP',
  interations = 'interation',
  trainset = 'trainset',
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
    keywords: data.keywords,
    trainSet: data.train_set,
    testSet: data.test_set,
    miningSet: data.mining_set,
    setsAccount: data.set_account,
    modelsAccount: data.models_account,
    ambition: data.flag ? {
      type: data.flag.type,
      value: data.flag.value,
    } : undefined,
    miningStrategy: data.mining_strategy,
    currentInteration: data.current_interation,
    createTime: data.create_datetime,
    desc: data.description,
  }
  return project
}

export function transferInteration (data: originInteration) {
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
