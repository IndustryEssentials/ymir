import { Iteration, } from "@/interface/project"
import { BackendData } from "@/interface/common"

export enum Stages {
  prepareMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  next = 5,
}
export enum MiningStrategy {
  block = 0,
  unique = 1,
  free = 2,
}

export function getStageLabel(stage: Stages, round: number = 0) {
  const labels = StageList().list.map(item => item.label)
  return `project.iteration.stage.${round ? labels[stage] : 'prepare'}`
}

type stageObject = {
  value: Stages,
  result?: string,
  url?: string,
}

export const StageList = () => {
  const iterationParams = 'iterationId={id}&currentStage={stage}&outputKey={output}&from=iteration'
  const list = [
    { label: 'ready', value: Stages.prepareMining, output: 'miningSet', input: '', url: `/home/project/{pid}/fusion?did={s0d}&strategy={s0s}&chunk={s0c}&${iterationParams}` },
    { label: 'mining', value: Stages.mining, output: 'miningResult', input: 'miningSet', url: `/home/project/{pid}/mining?did={s1d}&mid={s1m}&${iterationParams}` },
    { label: 'label', value: Stages.labelling, output: 'labelSet', input: 'miningResult', url: `/home/project/{pid}/label?did={s2d}&${iterationParams}` },
    { label: 'merge', value: Stages.merging, output: 'trainUpdateSet', input: 'labelSet', url: `/home/project/{pid}/merge?did={s3d}&merging={s3m}&${iterationParams}` },
    { label: 'training', value: Stages.training, output: 'model', input: 'trainUpdateSet', url: `/home/project/{pid}/train?did={s4d}&test={s4t}&${iterationParams}` },
    { label: 'next', value: Stages.next, output: '', input: 'trainSet', },
  ]
  return { list, ...singleList(list) }
}

export function transferIteration(data: BackendData): Iteration | undefined {
  if (!data) {
    return
  }
  return {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    round: data.iteration_round || 0,
    currentStage: data.current_stage || 0,
    testSet: data.validation_dataset_id || 0,
    miningSet: data.mining_input_dataset_id,
    miningResult: data.mining_output_dataset_id,
    labelSet: data.label_output_dataset_id,
    trainUpdateSet: data.training_input_dataset_id,
    model: data.training_output_model_id,
    trainSet: data.previous_training_dataset_id,
    prevIteration: data.previous_iteration || 0,
  }
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

type Ratio = {
  class_name: string,
  processed_assets_count: number,
  total_assets_count: number,
}

export function transferMiningStats(data: BackendData) {
  const { total_mining_ratio, class_wise_mining_ratio, negative_ratio } = data
  const transfer = (ratios: Array<Ratio>) => {
    const getName = (ratio: Ratio) => ratio.class_name || ''
    const keywords  = ratios.map(getName)
    const count = ratios.reduce((prev, item) => {
      const name = getName(item)
      return {
        ...prev,
        [name]: item.processed_assets_count,
        [name + '_total']: item.total_assets_count,
      }
    }, {})
    return {
      keywords,
      count,
    }
  }
  return {
    totalList: transfer([total_mining_ratio]),
    keywordList: transfer(class_wise_mining_ratio),
  }
}
