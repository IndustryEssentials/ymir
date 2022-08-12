import { getLocale } from "umi"
import { DatasetGroup, Dataset, DatasetAnalysis, Annotation, Asset } from "@/interface/dataset"
import { calDuration, format } from '@/utils/date'
import { getIterationVersion, transferIteration } from "./project"
import { BackendData } from "@/interface/common"

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
    versionName: getIterationVersion(data.version_num),
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
    progress: data.related_task.percent || 0,
    taskState: data.related_task.state,
    taskType: data.related_task.type,
    duration: data.related_task.duration,
    durationLabel: calDuration(data.related_task.duration, getLocale()),
    taskName: data.related_task.name,
    task: data.related_task,
    hidden: !data.is_visible,
    description: data.description || '',
  }
}

export function transferDatasetAnalysis(data: BackendData): DatasetAnalysis {
  const { asset_bytes, asset_area, asset_quality, asset_hw_ratio, } = data.hist

  const assetTotal = data.total_assets_count || 0
  const gt = generateAnno(data.gt)
  const pred = generateAnno(data.pred)
  return {
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getIterationVersion(data.version_num),
    assetCount: assetTotal,
    totalAssetMbytes: data.total_assets_mbytes,
    assetBytes: asset_bytes,
    assetArea: asset_area,
    assetQuality: asset_quality,
    assetHWRatio: asset_hw_ratio,
    gt,
    pred,
    cks: transferCK(data.cks_count, data.cks_count_total),
    tags: transferCK(data.tags_count, data.tags_count_total),
  }
}

export function transferAsset(data: BackendData, keywords: Array<string>): Asset {
  const transferAnnotations = (annotations = [], gt = false) =>
    annotations.map((an: BackendData) => transferAnnotation(an, gt))
  const annotations = [
    ...transferAnnotations(data.gt, true),
    ...transferAnnotations(data.pred),
  ].map(annotation => ({ ...annotation, color: generateColor(annotation.keyword, keywords || data.keywords) }))
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
  }
}

export function transferAnnotation(data: BackendData, gt: boolean = false): Annotation {
  return {
    ...data,
    keyword: data.keyword,
    box: data.box,
    cm: data.cm,
    gt,
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
  const { anno_quality, anno_area, anno_area_ratio } = data.hist
  return {
    keywords: data.keywords,
    total: data.annos_count,
    average: data.ave_annos_count,
    negative: data.negative_assets_count,
    quality: anno_quality,
    area: anno_area,
    areaRatio: anno_area_ratio,
  }
}

function generateColor(keyword: string, keywords: Array<string> = []) {
  const KeywordColor = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"]
  const colors: { [key: string]: any } = keywords.reduce((prev, curr, i) =>
    ({ ...prev, [curr]: KeywordColor[i % KeywordColor.length] }), {})
  return colors[keyword]
}
