import { getLocale } from 'umi'
import { calDuration, format } from '@/utils/date'
import { getVersionLabel } from './common'
import { ObjectType } from './project'

export enum AnnotationType {
  BoundingBox = 0,
  Polygon = 1,
  Mask = 2,
}

export enum MergeType {
  New = 0,
  Exist = 1,
}

export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

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

export const statesLabel = (state: states) => {
  const maps = {
    [states.READY]: 'dataset.state.ready',
    [states.VALID]: 'dataset.state.valid',
    [states.INVALID]: 'dataset.state.invalid',
  }
  return maps[state]
}

export enum IMPORTSTRATEGY {
  ALL_KEYWORDS_IGNORE = 1,
  UNKOWN_KEYWORDS_IGNORE = 2,
  UNKOWN_KEYWORDS_STOP = 3,
  UNKOWN_KEYWORDS_AUTO_ADD = 4,
}

export enum MERGESTRATEGY {
  NORMAL = 0,
  HOST = 1,
  GUEST = 2,
}

export enum MERGESTRATEGYFORTRAIN {
  STOP = 0,
  ASTRAIN = 1,
  ASVALIDATION = 2,
}

export function transferDatasetGroup(data: YModels.BackendData) {
  const group: YModels.DatasetGroup = {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    createTime: format(data.create_datetime),
    versions: data.datasets ? data.datasets.map((ds: YModels.BackendData) => transferDataset(ds)) : [],
  }
  return group
}

export function transferDataset(data: YModels.BackendData): YModels.Dataset {
  const { gt = {} } = data.keywords
  const assetCount = data.asset_count || 0
  const keywords = Object.keys(gt)
  return {
    id: data.id,
    groupId: data.dataset_group_id,
    projectId: data.project_id,
    type: data.object_type || ObjectType.ObjectDetection,
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getVersionLabel(data.version_num),
    assetCount,
    keywords,
    keywordCount: keywords.length,
    gt: transferAnnotationsCount(gt, data.negative_info?.gt, assetCount),
    isProtected: data.is_protected || false,
    hash: data.hash,
    state: data.result_state,
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
    taskId: data.task_id,
    progress: data.related_task.percent || 0,
    taskState: data.related_task.state,
    taskType: data.related_task.type,
    duration: data.related_task.duration,
    durationLabel: calDuration(data.related_task.duration, getLocale()),
    taskName: data.related_task.name,
    task: data.related_task,
    hidden: !data.is_visible,
    description: data.description || '',
    cks: data.cks_count ? transferCK(data.cks_count, data.cks_count_total) : undefined,
    tags: data.gt
      ? transferCK(data?.gt?.tags_count, data?.gt?.tags_count_total)
      : undefined,
  }
}

export function validDataset(dataset: YModels.Dataset | undefined) {
  return dataset && dataset.state === states.VALID
}

export function runningDataset(dataset: YModels.Dataset | undefined) {
  return dataset && dataset.state === states.READY
}

export function canHide(dataset: YModels.Dataset, project: YModels.Project | undefined) {
  const p = project || dataset.project
  return !runningDataset(dataset) && !p?.hiddenDatasets?.includes(dataset.id)
}

export function transferDatasetAnalysis(data: YModels.BackendData): YModels.DatasetAnalysis {
  const { bytes, area, quality, hw_ratio } = data.hist

  const gt = generateAnno(data.gt)
  const pred = generateAnno(data.pred)
  const dataset = transferDataset(data)
  return {
    ...dataset,
    assetArea: area,
    assetQuality: quality,
    assetHWRatio: hw_ratio,
    gt,
    pred,
    cks: transferCK(data.cks_count, data.cks_count_total),
    tags: transferCK(data.gt.tags_count, data.gt?.tags_count_total),
  }
}

export function transferAnnotationsCount(count = {}, negative = 0, total = 1) {
  return {
    keywords: Object.keys(count),
    count,
    negative,
    total,
  }
}

const transferCK = (counts: YModels.BackendData = {}, total: YModels.BackendData = {}): YModels.CKCounts => {
  let subKeywordsTotal = 0
  const keywords = Object.keys(counts).map((keyword: string) => {
    const children: { [key: string]: number } = counts[keyword]
    const subList = Object.keys(children)
    const count: number = total[keyword]
    subKeywordsTotal += subList.length
    return {
      keyword,
      children: subList.map((child: string) => ({
        keyword: child,
        count: children[child] || 0,
      })),
      count: count || 0,
    }
  })
  return {
    keywords,
    counts,
    subKeywordsTotal,
    total,
  }
}

const generateAnno = (data: YModels.BackendData): YModels.AnylysisAnnotation => {
  const { quality = [], area = [], box_area_ratio = [], mask_area = [], obj_counts = [], class_counts = [] } = data.hist
  return {
    keywords: data.keywords,
    total: data.annos_count || 0,
    average: data.ave_annos_count || 0,
    negative: data.negative_assets_count || 0,
    quality: quality || [],
    areaRatio: box_area_ratio || [],
    keywordAnnotaitionCount: data.classwise_annos_count || {},
    totalArea: data.total_mask_area || 0,
    keywordArea: data.classwise_area || {},
    instanceArea: mask_area,
    crowdedness: obj_counts,
    complexity: class_counts,
  }
}
