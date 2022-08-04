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
  const { negative_images_cnt = 0, project_negative_images_cnt = 0 } = data.negative_info || {}
  return {
    id: data.id,
    groupId: data.dataset_group_id,
    projectId: data.project_id,
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getIterationVersion(data.version_num),
    assetCount: data.asset_count || 0,
    keywords: Object.keys(data.keywords || {}),
    keywordCount: data.keyword_count || 0,
    keywordsCount: data.keywords || {},
    nagetiveCount: negative_images_cnt,
    isProtected: data.is_protected || false,
    projectNagetiveCount: project_negative_images_cnt,
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
  return {
    name: data.group_name,
    version: data.version_num || 0,
    versionName: getIterationVersion(data.version_num),
    assetCount: data.total_assets_cnt || 0,
    totalAssetMbytes: data.total_asset_mbytes,
    annosCnt: data.annos_cnt,
    aveAnnosCnt: data.ave_annos_cnt,
    positiveAssetCnt: data.positive_asset_cnt,
    negativeAssetCnt: data.negative_asset_cnt,
    assetBytes: data.asset_bytes,
    assetHWRatio: data.asset_hw_ratio,
    assetArea: data.asset_area,
    assetQuality: data.asset_quality,
    annoAreaRatio: data.anno_area_ratio,
    annoQuality: data.anno_quality,
    classNamesCount: data.class_names_count,
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

function generateColor(keyword: string, keywords: Array<string> = []) {
  console.log('generateColor keywords:', keywords)
  const KeywordColor = ["green", "red", "cyan", "blue", "yellow", "purple", "magenta", "orange", "gold"]
  const colors: { [key: string]: any } = keywords.reduce((prev, curr, i) =>
    ({ ...prev, [curr]: KeywordColor[i % KeywordColor.length] }), {})
  return colors[keyword]
}
