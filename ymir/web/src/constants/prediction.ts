import { getLocale } from 'umi'
import { calDuration, format } from '@/utils/date'
import { getVersionLabel } from './common'
import { ObjectType } from './project'
import { transferAnnotationsCount } from './dataset'

export enum evaluationTags {
  tp = 1,
  fp = 2,
  fn = 3,
  mtp = 11,
}

export const evaluationLabel = (tag: evaluationTags) => {
  const maps = {
    [evaluationTags.tp]: 'tp',
    [evaluationTags.fp]: 'fp',
    [evaluationTags.fn]: 'fn',
    [evaluationTags.mtp]: 'mtp',
  }
  return maps[tag]
}

export function transferPrediction(data: YModels.BackendData): YModels.Prediction {
  const task = data.related_task
  const params = task?.parameters
  const config = task?.config || {}
  const { gt = {}, pred = {} } = data.keywords
  const assetCount = data.asset_count || 0
  const keywords = [...new Set([...Object.keys(gt), ...Object.keys(pred)])]
  const evaluated = data.evaluation_state === 1
  return {
    id: data.id,
    projectId: data.project_id,
    type: data.object_type || ObjectType.ObjectDetection,
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getVersionLabel(data.version_num),
    assetCount,
    keywords,
    keywordCount: keywords.length,
    gt: transferAnnotationsCount(gt, data.negative_info?.gt, assetCount),
    pred: transferAnnotationsCount(pred, data.negative_info?.pred, assetCount),
    isProtected: data.is_protected || false,
    hash: data.hash,
    state: data.result_state,
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
    taskId: data.task_id,
    progress: task.percent || 0,
    taskState: task.state,
    taskType: task.type,
    duration: task.duration,
    durationLabel: calDuration(task.duration, getLocale()),
    taskName: task.name,
    task,
    hidden: !data.is_visible,
    description: data.description || '',
    inferClass: data?.keywords?.eval_class_ids || data?.pred?.eval_class_ids,
    evaluated,
    inferModelId: [params?.model_id || 0, params?.model_stage_id || 0],
    inferDatasetId: params?.dataset_id || 0,
    inferConfig: config,
    rowSpan: data.rowSpan,
    odd: data.odd,
  }
}
