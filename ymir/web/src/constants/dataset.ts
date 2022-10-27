import { getLocale } from "umi"
import { DatasetGroup, Dataset, DatasetAnalysis, Annotation, Asset } from "@/interface/dataset"
import { calDuration, format } from '@/utils/date'
import { getVersionLabel } from "./common"
import { BackendData } from "@/interface/common"
import { Project } from "@/interface/project"
import { humanize } from "@/utils/number"

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

export function transferDatasetGroup(data: BackendData) {
  const group: DatasetGroup = {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    createTime: format(data.create_datetime),
    versions: data.datasets ? data.datasets.map((ds: BackendData) => transferDataset(ds)) : [],
  }
  return group
}


const tagsCounts = (gt: BackendData = {}, pred: BackendData = {}) => Object.keys(gt).reduce((prev, tag) => {
  const gtCount = gt[tag] || {}
  const predCount = pred[tag] || {}
  return { ...prev, [tag]: { ...gtCount, ...predCount } }
}, {})
const tagsTotal = (gt: BackendData = {}, pred: BackendData = {}) => ({ ...gt, ...pred })

export function transferDataset(data: BackendData): Dataset {
  const { gt = {}, pred = {} } = data.keywords
  const assetCount = data.asset_count || 0
  const keywords = [...new Set([...Object.keys(gt), ...Object.keys(pred)])]
  return {
    id: data.id,
    groupId: data.dataset_group_id,
    projectId: data.project_id,
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getVersionLabel(data.version_num),
    assetCount,
    humanizeAssetCount: humanize(assetCount),
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
    progress: data.related_task.percent || 0,
    taskState: data.related_task.state,
    taskType: data.related_task.type,
    duration: data.related_task.duration,
    durationLabel: calDuration(data.related_task.duration, getLocale()),
    taskName: data.related_task.name,
    task: data.related_task,
    hidden: !data.is_visible,
    description: data.description || '',
    inferClass: data?.pred?.eval_class_ids,
    cks: data.cks_count ? transferCK(data.cks_count, data.cks_count_total) : undefined,
    tags: data.gt ? transferCK(tagsCounts(data?.gt?.tags_count, data?.pred?.tags_count), tagsTotal(data?.gt?.tags_count_total, data?.pred?.tags_count_total)) : undefined,
  }
}

export function validDataset(dataset: Dataset | undefined) {
  return dataset && dataset.state === states.VALID
}

export function runningDataset(dataset: Dataset | undefined) {
  return dataset && dataset.state === states.READY
}

export function canHide(dataset: Dataset, project: Project | undefined) {
  const p = project || dataset.project
  return !runningDataset(dataset) && !p?.hiddenDatasets?.includes(dataset.id)
}

export function transferDatasetAnalysis(data: BackendData): DatasetAnalysis {
  const { bytes, area, quality, hw_ratio, } = data.hist

  const assetTotal = data.total_assets_count || 0
  const gt = generateAnno(data.gt)
  const pred = generateAnno(data.pred)
  return {
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getVersionLabel(data.version_num),
    assetCount: assetTotal,
    totalAssetMbytes: data.total_assets_mbytes,
    assetBytes: bytes,
    assetArea: area,
    assetQuality: quality,
    assetHWRatio: hw_ratio,
    gt,
    pred,
    inferClass: data?.pred?.eval_class_ids,
    cks: transferCK(data.cks_count, data.cks_count_total),
    tags: transferCK(tagsCounts(data.gt.tags_count, data.pred?.tags_count), tagsTotal(data.gt?.tags_count_total, data.pred?.tags_count_total)),
  }
}

export function transferAsset(data: BackendData, keywords: Array<string>): Asset {
  const colors = generateDatasetColors(keywords || data.keywords)
  const transferAnnotations = (annotations = [], gt = false) => 
    annotations.map((an: BackendData) => transferAnnotation(an, gt, colors[an.keyword]))

  const annotations = [
    ...transferAnnotations(data.gt, true),
    ...transferAnnotations(data.pred),
  ]
  const evaluated = annotations.some(annotation => evaluationTags[annotation.cm])
  return {
    id: data.id,
    hash: data.hash,
    keywords: data.keywords || [],
    url: data.url,
    metadata: data.metadata,
    size: data.size,
    annotations,
    evaluated: evaluated,
    cks: data.cks || {},
  }
}

export function transferAnnotation(data: BackendData, gt: boolean = false, color = ''): Annotation {
  return {
    ...data,
    keyword: data.keyword,
    box: data.box,
    cm: data.cm,
    gt,
    tags: data.tags || {},
    color,
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

const transferCK = (counts: BackendData = {}, total: BackendData = {}) => {
  const keywords = Object.keys(counts).map(keyword => {
    const children = counts[keyword]
    return {
      keyword,
      children: Object.keys(children).map(child => ({
        keyword: child,
        count: children[child],
      })),
      count: total[keyword],
    }
  })
  return {
    keywords,
    counts,
    total,
  }
}

const generateAnno = (data: BackendData) => {
  const { quality, area, area_ratio } = data.hist
  return {
    keywords: data.keywords,
    total: data.annos_count,
    average: data.ave_annos_count,
    negative: data.negative_assets_count,
    quality: quality,
    area: area,
    areaRatio: area_ratio,
  }
}

function generateDatasetColors(keywords: Array<string> = []): {[name: string]: string} {
  const KeywordColor = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"]
  return keywords.reduce((prev, curr, i) =>
    ({ ...prev, [curr]: KeywordColor[i % KeywordColor.length] }), {})
}
