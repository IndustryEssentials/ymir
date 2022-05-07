import { getLocale } from "umi"
import { DatasetGroup, Dataset } from "@/interface/dataset"
import { calDuration, format } from '@/utils/date'
import { getIterationVersion, transferIteration } from "./project"
import { BackendData } from "@/interface/common"

export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export const statesLabel = (state: states) => {
  const maps = {
    [states.READY]: 'dataset.state.ready',
    [states.VALID]: 'dataset.state.valid',
    [states.INVALID]: 'dataset.state.invalid',
  }
  return maps[state]
} 

export function transferDatasetGroup (data: BackendData) {
  const group: DatasetGroup = {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    createTime: format(data.create_datetime),
    versions: data.datasets ? data.datasets.map((ds: BackendData) => transferDataset(ds)) : [],
  }
  return group
}

export function transferDataset (data: BackendData): Dataset {
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
    ignoredKeywords: Object.keys(data.ignored_keywords || {}),
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
  }
}
