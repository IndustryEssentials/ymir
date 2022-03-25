import { Project, originProject, originIteration, Iteration, } from "@/interface/project"
import { format } from '@/utils/date'

export enum Stages {
  beforeMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  trained = 5,
}
type stageObject = {
  value: Stages,
  result?: string,
  url?: string,
}
export const StageList = () => {
  const list = [
    { value: Stages.beforeMining, prepare: 'trainSet', resultKey: 'miningSet', url: '/home/task/fusion/' },
    { value: Stages.mining, prepare: 'miningSet', resultKey: 'miningResult', url: '/home/task/mining/' },
    { value: Stages.labelling, prepare: 'miningResult', resultKey: 'labelSet', url: '/home/task/label/' },
    { value: Stages.merging, prepare: 'labelSet', resultKey: 'trainUpdateSet', url: '/home/task/fusion/' },
    { value: Stages.training, prepare: 'trainUpdateSet', resultKey: 'model', url: '/home/task/training/' },
    { value: Stages.trained, prepare: 'trainUpdateSet', resultKey: 'trainSet', },
  ]
  return { list, ...singleList(list) }
}

export function getIterationVersion(version: number) {
  return `V${version}`
}

export function transferProject(data: originProject) {
  const project: Project = {
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
    currentIteration: data.current_iteration_id || 0,
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.training_type,
    targetMap: data.map_target,
    targetDataset: data.training_dataset_count_target,
    targetIteration: data.iteration_target || 0,
    updateTime: format(data.update_datetime),
  }
  return project
}

type mapObject = {
  name: string,
  origin: string,
  def?: any,
}
interface dataObject {
  [key: string]: any,
}

export function transferIteration(data: dataObject) {
  if (!data) {
    return {}
  }
  const maps = [
    { name: 'id', origin: 'id', def: 0 },
    { name: 'name', origin: 'name', def: '' },
    { name: 'round', origin: 'iteration_round', def: 0 },
    { name: 'current', origin: 'current_stage', def: 0 },
    { name: 'miningSet', origin: 'mining_input_dataset_id', def: 0 },
    { name: 'miningResult', origin: 'mining_output_dataset_id', def: 0 },
    { name: 'labelSet', origin: 'label_output_dataset_id', def: 0 },
    { name: 'trainUpdateSet', origin: 'training_input_dataset_id', def: 0 },
    { name: 'model', origin: 'training_output_model_id', def: 0 },
    { name: 'trainSet', origin: 'previous_training_dataset_id', def: 0 },
  ]
  return transferData(maps, data)
}
export function transferData(maps: Array<mapObject>, data: dataObject) {
  return maps.reduce((prev, curr, index) => {
    return {
      ...prev,
      [curr.name]: data[curr.origin] || curr.def,
    }
  }, {})
}

function singleList(arr: Array<stageObject>) {
  return arr.reduce((prev, item, index) => ({
    ...prev,
    [item.value]: {
      ...item,
      next: arr[index + 1] ? arr[index + 1] : null,
    }
  }), {})
}
