import { transferDatasetGroup, transferDataset } from '@/constants/dataset'
import { format } from '@/utils/date'
import { transferIteration } from './iteration'

export enum PROJECTTYPES {
  Classification = 1,
  ObjectDetection = 2,
  SemanticSegmentation = 3,
}

const typesPrefix = 'project.types.'
const projectTypes = [
  { label: 'det', value: PROJECTTYPES.ObjectDetection },
  { label: 'seg', value: PROJECTTYPES.SemanticSegmentation },
]

export const getProjectTypes = () => projectTypes.map(({ label, value }) => ({ label: typesPrefix + label, value }))

export const getProjectTypeLabel = (type: PROJECTTYPES, prefix: boolean = false) => {
  const target = projectTypes.find(({ value }) => value === type)
  return (prefix ? typesPrefix : '') + target?.label
}

export const tabs = [
  { tab: 'project.tab.set.title', key: 'dataset' },
  { tab: 'project.tab.model.title', key: 'model' },
]

export function transferProject(data: YModels.BackendData) {
  const iteration = transferIteration(data.current_iteration)
  const project: YModels.Project = {
    id: data.id,
    name: data.name,
    keywords: data.training_keywords,
    trainSet: data.training_dataset_group ? transferDatasetGroup(data.training_dataset_group) : undefined,
    testSet: data.validation_dataset ? transferDataset(data.validation_dataset) : undefined,
    miningSet: data.mining_dataset ? transferDataset(data.mining_dataset) : undefined,
    testingSets: data.testing_dataset_ids ? data.testing_dataset_ids.split(',').map(Number) : [],
    setCount: data.dataset_count,
    candidateTrainSet: data.candidate_training_dataset_id || 0,
    trainSetVersion: data.initial_training_dataset_id || 0,
    model: data.initial_model_id || 0,
    modelStage: data.initial_model_id ? [data.initial_model_id, data.initial_model_stage_id] : undefined,
    modelCount: data.model_count,
    miningStrategy: data.mining_strategy,
    chunkSize: data.chunk_size,
    currentIteration: iteration,
    currentStep: iteration?.currentStep?.name || '',
    round: iteration?.round || 0,
    isExample: data.is_example || false,
    createTime: format(data.create_datetime),
    description: data.description,
    type: data.object_type,
    typeLabel: getProjectTypeLabel(data.object_type, true),
    hiddenDatasets: data.referenced_dataset_ids || [],
    hiddenModels: data.referenced_model_ids || [],
    updateTime: format(data.update_datetime),
    enableIteration: data.enable_iteration,
    totalAssetCount: data.total_asset_count,
    runningTaskCount: data.running_task_count,
    totalTaskCount: data.total_task_count,
  }
  return project
}
