export enum Stages {
  prepareMining = 0,
  mining = 1,
  labelling = 2,
  merging = 3,
  training = 4,
  next = 5,
}

export enum STEP {
  prepareMining = "prepare_mining",
  mining = "mining",
  labelling = "label",
  merging = "prepare_training",
  training = "training",
  next = "next",
}

export enum MiningStrategy {
  block = 0,
  unique = 1,
  free = 2,
}

export function getStepLabel(step: STEP, round: number = 0) {
  const list = getSteps()
  const target = list.find((item) => item.value === step)
  return `project.iteration.stage.${round ? target?.label : "prepare"}`
}

type StepObj = {
  label: string
  value: STEP
  unskippable?: boolean
  act?: string
  react?: string
  state?: number
}

export const getSteps = (): StepObj[] => {
  const glabels = (label: string) => `project.iteration.stage.${label}`
  const list = [
    { label: "ready", value: STEP.prepareMining },
    { label: "mining", value: STEP.mining },
    { label: "label", value: STEP.labelling },
    { label: "merge", value: STEP.merging, unskippable: true },
    { label: "training", value: STEP.training, unskippable: true },
    { label: "next", value: STEP.next },
  ]
  return list.map((item, index) => {
    const label = glabels(item.label)
    const ind = index + 1
    return {
      ...item,
      act: label,
      react: `${label}.react`,
      state: -1,
      index: ind,
      next: list[ind]?.value,
    }
  })
}

export function transferIteration(
  data: YModels.BackendData
): YModels.Iteration | undefined {
  if (!data) {
    return
  }
  return {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    round: data.iteration_round || 0,
    currentStep: transferStep(data.current_step),
    steps: (data.iteration_steps || []).map(transferStep),
    currentStage: data.current_stage || 0,
    testSet: data.validation_dataset_id || 0,
    wholeMiningSet: data.mining_dataset_id || 0,
    miningSet: data.mining_input_dataset_id,
    miningResult: data.mining_output_dataset_id,
    labelSet: data.label_output_dataset_id,
    trainUpdateSet: data.training_input_dataset_id,
    model: data.training_output_model_id,
    trainSet: data.previous_training_dataset_id,
    prevIteration: data.previous_iteration || 0,
  }
}

function transferStep(data: YModels.BackendData = {}): YModels.Step {
  return {
    id: data.id,
    finished: data.is_finished,
    name: data.name,
    percent: data.percent,
    preSetting: data.presetting,
    state: data.state,
    taskId: data.task_id,
    taskType: data.task_type,
  }
}

type Ratio = {
  class_name: string
  processed_assets_count: number
  total_assets_count: number
}

export function transferMiningStats(data: YModels.BackendData) {
  const { total_mining_ratio, class_wise_mining_ratio, negative_ratio } = data
  const transfer = (ratios: Array<Ratio>) => {
    const getName = (ratio: Ratio) => ratio.class_name || ""
    const keywords = ratios.map(getName)
    const count = ratios.reduce((prev, item) => {
      const name = getName(item)
      return {
        ...prev,
        [name]: item.processed_assets_count,
        [name + "_total"]: item.total_assets_count,
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
