import { getLocale } from 'umi'
import { calDuration, format } from '@/utils/date'
import { getVersionLabel } from './common'
import { ObjectType } from './project'
import { transferSuggestion } from './datasetAnalysis'
import { Backend, Dataset, DatasetGroup, DatasetSuggestions, Project } from '.'
import { AnalysisChartData, CKCounts, DatasetAnalysis, KeywordCountsType } from './typings/dataset.d'

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

export function transferDatasetGroup(data: Backend) {
  const group: DatasetGroup = {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    createTime: format(data.create_datetime),
    versions: data.datasets ? data.datasets.reverse().map(transferDataset) : [],
  }
  return group
}

export function transferDataset(data: Backend): Dataset {
  const { gt = {} } = data.keywords
  const assetCount = data.asset_count || 0
  const keywords = Object.keys(gt)
  const analysis = data?.analysis || {}
  const suggestions = [
    { source: 'class_proportion', key: 'classBias', type: 'keyword' },
    { source: 'class_obj_count', key: 'annotationCount', type: 'keyword' },
    { source: 'density_proportion', key: 'annotationDensity' },
  ].reduce<DatasetSuggestions>((prev, { key, source, type }) => {
    const suggest = transferSuggestion(analysis[source], type)
    return suggest ? { ...prev, [key]: suggest } : prev
  }, {})
  const versionName = getVersionLabel(data.version_num)
  return {
    id: data.id,
    groupId: data.dataset_group_id,
    projectId: data.project_id,
    type: data.object_type || ObjectType.ObjectDetection,
    name: `${data.group_name} ${versionName}`,
    version: data.version_num || 0,
    versionName,
    assetCount,
    keywords,
    keywordCount: keywords.length,
    gt: transferAnnotationsCount(gt, data.gt?.negative_assets_count, assetCount),
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
    tags: data.gt?.tags_count ? transferCK(data?.gt?.tags_count, data?.gt?.tags_count_total) : undefined,
    suggestions,
  }
}

export function validDataset(dataset?: Dataset) {
  return dataset && dataset.state === states.VALID
}

export function runningDataset(dataset?: Dataset) {
  return dataset && dataset.state === states.READY
}

export function canHide(dataset: Dataset, project: Project | undefined) {
  const p = project || dataset.project
  return !runningDataset(dataset) && !p?.hiddenDatasets?.includes(dataset.id)
}

export function transferDatasetAnalysis(data: Backend): DatasetAnalysis {
  const { bytes, area, quality, hw_ratio } = data.hist
  const gt = data.gt
  const { quality: gtQuality = [], box_area_ratio = [], mask_area = [], obj_counts = [], class_counts = [] } = gt.hist

  const dataset = transferDataset(data)
  const keywords = dataset.keywords
  const total = dataset.gt?.total
  const totalArea = data.gt?.total_mask_area || 0
  const assetCount = dataset.assetCount
  const annoCount = gt?.annos_count || 0
  return {
    ...dataset,
    total: gt?.annos_count || 0,
    negative: gt.negative_assets_count || 0,
    average: data.gt?.ave_annos_count || 0,
    totalArea,
    keywordCounts: keywords2ChartData(dataset.keywords, dataset.assetCount, dataset.gt?.count),
    assetArea: addTotal2ChartData(area, assetCount),
    assetQuality: addTotal2ChartData(quality, assetCount),
    assetHWRatio: addTotal2ChartData(hw_ratio, assetCount),
    quality: addTotal2ChartData(gtQuality, assetCount),
    areaRatio: addTotal2ChartData(box_area_ratio, annoCount),
    keywordAnnotationCount: keywords2ChartData(keywords, annoCount, gt.classwise_annos_count),
    keywordArea: keywords2ChartData(keywords, totalArea, gt?.classwise_area),
    instanceArea: addTotal2ChartData(mask_area, total),
    crowdedness: addTotal2ChartData(obj_counts, assetCount),
    complexity: addTotal2ChartData(class_counts, assetCount),
  }
}

const keywords2ChartData = (list: string[] = [], total?: number, counts: KeywordCountsType = {}) => ({
  data: list.map((item) => ({
    x: item,
    y: counts[item] || 0,
  })),
  total,
})

const addTotal2ChartData = (list: AnalysisChartData[] = [], total?: number) => ({ data: list, total })

export function transferAnnotationsCount(count: KeywordCountsType = {}, negative = 0, total = 1) {
  return {
    keywords: Object.keys(count),
    count,
    negative,
    total,
  }
}

const transferCK = (counts: Backend = {}, total: Backend = {}): CKCounts => {
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
