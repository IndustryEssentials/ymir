import { Project, Iteration, } from "@/interface/project"
import { BackendData } from "@/interface/common"
import { transferDatasetGroup, transferDataset } from '@/constants/dataset'
import { format } from '@/utils/date'

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

export const tabs = [
  { tab: 'project.tab.set.title', key: 'dataset', },
  { tab: 'project.tab.model.title', key: 'model', },
]

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
  const iterationParams = 'iterationId={id}&currentStage={stage}&outputKey={output}'
  const list = [
    { label: 'ready', value: Stages.prepareMining, output: 'miningSet', input: '', url: `/home/task/fusion/{pid}?did={s0d}&strategy={s0s}&chunk={s0c}&${iterationParams}` },
    { label: 'mining', value: Stages.mining, output: 'miningResult', input: 'miningSet', url: `/home/task/mining/{pid}?did={s1d}&mid={s1m}&${iterationParams}` },
    { label: 'label', value: Stages.labelling, output: 'labelSet', input: 'miningResult', url: `/home/task/label/{pid}?did={s2d}&${iterationParams}` },
    { label: 'merge', value: Stages.merging, output: 'trainUpdateSet', input: 'labelSet', url: `/home/task/fusion/{pid}?did={s3d}&merging={s3m}&${iterationParams}` },
    { label: 'training', value: Stages.training, output: 'model', input: 'trainUpdateSet', url: `/home/task/train/{pid}?did={s4d}&test={s4t}&${iterationParams}` },
    { label: 'next', value: Stages.next, output: '', input: 'trainSet', },
  ]
  return { list, ...singleList(list) }
}

export function getIterationVersion(version: number) {
  return `V${version}`
}

export function transferProject(data: BackendData) {
  const iteration = transferIteration(data.current_iteration)
  const project: Project = {
    id: data.id,
    name: data.name,
    keywords: data.training_keywords,
    trainSet: data.training_dataset_group ? transferDatasetGroup(data.training_dataset_group) : undefined,
    testSet: data.testing_dataset ? transferDataset(data.testing_dataset) : undefined,
    miningSet: data.mining_dataset ? transferDataset(data.mining_dataset) : undefined,
    setCount: data.dataset_count,
    trainSetVersion: data.initial_training_dataset_id || 0,
    model: data.initial_model_id || 0,
    modelCount: data.model_count,
    miningStrategy: data.mining_strategy,
    chunkSize: data.chunk_size,
    currentIteration: iteration,
    currentStage: iteration?.currentStage || 0,
    round: iteration?.round || 0,
    isExample: data.is_example || false,
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.training_type,
    hiddenDatasets: data.referenced_dataset_ids || [],
    hiddenModels: data.referenced_model_ids || [],
    updateTime: format(data.update_datetime),
  }
  return project
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
    testSet: data.testing_dataset_id || 0,
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
