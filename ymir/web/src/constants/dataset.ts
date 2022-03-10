import { OriginDatasetGroup, DatasetGroup, OriginDataset, Dataset } from "@/interface/dataset"
import { format } from '@/utils/date'
import { getInterationVersion } from "./project"

export enum states {
  READY = 1,
  VALID = 2,
  INVALID = 3,
}

export function transferDatasetGroup (data: OriginDatasetGroup) {
  const group: DatasetGroup = {
    id: data.id,
    projectId: data.project_id,
    name: data.name,
    createTime: format(data.create_datetime),
  }
  return group
}

export function transferDataset (data: OriginDataset): Dataset {
  return {
    id: data.id,
    groupId: data.dataset_group_id,
    projectId: data.project_id,
    name: data.name,
    version: data.version_num || 0,
    versionName: getInterationVersion(data.version_num),
    assetCount: data.asset_count || 0,
    keywords: data.keywords || [],
    keywordCount: data.keyword_count || 0,
    ignoredKeywords: data.ignored_keywords || [],
    hash: data.hash,
    state: data.state,
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
    taskId: data.task_id,
    progress: data.related_task.percent || 0,
    taskState: data.related_task.state,
    taskType: data.related_task.type,
    duration: data.related_task.duration,
    taskName: data.related_task.name,
  }
}
