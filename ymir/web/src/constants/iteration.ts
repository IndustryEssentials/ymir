export enum Stages {
  prepareMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  next = 5,
}

export enum STEP {
  prepareMining = 'prepare_mining',
  mining = 'mining',
  labelling = 'label',
  merging = 'prepare_training',
  training = 'training',
  next = 'next',
}

export enum MiningStrategy {
  block = 0,
  unique = 1,
  free = 2,
}

export function getStepLabel(step: STEP | undefined, round: number = 0) {
  const list = getSteps()
  const target = list.find((item) => item.value === (step || STEP.next))
  return `project.iteration.stage.${round ? target?.label : 'prepare'}`
}

type StepObj = {
  label: string
  value: STEP
  unskippable?: boolean
  act?: string
  react?: string
  state?: number
  index: number
}

export const getSteps = (): StepObj[] => {
  const glabels = (label: string) => `project.iteration.stage.${label}`
  const list = [
    { label: 'ready', value: STEP.prepareMining },
    { label: 'mining', value: STEP.mining },
    { label: 'label', value: STEP.labelling },
    { label: 'merge', value: STEP.merging, unskippable: true },
    { label: 'training', value: STEP.training, unskippable: true },
    { label: 'next', value: STEP.next },
  ]
  return list.map((item, index) => {
    const label = glabels(item.label)
    const ind: number = index
    const end = index + 1 === list.length
    return {
      ...item,
      act: label,
      react: !end ? `${label}.react` : '',
      state: -1,
      index: ind,
      next: list[ind]?.value,
      end,
    }
  })
}

export function transferIteration(data: YModels.BackendData): YModels.Iteration | undefined {
  if (!data) {
    return
  }
  const currentStep = transferStep(data?.current_step)
  return {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    round: data.iteration_round || 0,
    currentStep,
    steps: (data.iteration_steps || []).map(transferStep),
    testSet: data.validation_dataset_id || 0,
    wholeMiningSet: data.mining_dataset_id || 0,
    prevIteration: data.previous_iteration || 0,
    model: data.training_output_model_id,
    end: !currentStep,
  }
}

function transferStep(data: YModels.BackendData): YModels.Step | undefined {
  if (!data) {
    return
  }

  return {
    id: data.id,
    finished: data.is_finished,
    name: data.name,
    percent: data.percent,
    preSetting: data.presetting,
    state: data.state,
    taskId: data.task_id,
    taskType: data.task_type,
    resultId: data?.result?.id,
    resultType: data?.result?.result_type == 1 ? 'dataset' : 'model',
  }
}

type Ratio = {
  class_name: string
  processed_assets_count: number
  total_assets_count: number
}

export function transferMiningStats(data: YModels.BackendData): YModels.MiningStats {
  const { total_mining_ratio, class_wise_mining_ratio, negative_ratio } = data
  const transfer = (ratios: Array<Ratio>) => {
    const getName = (ratio: Ratio) => ratio.class_name || ''
    const keywords = ratios.map(getName)
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
