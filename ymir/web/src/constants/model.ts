import { OriginModelGroup, ModelGroup, OriginModelVersion, ModelVersion } from "@/interface/model"
import { format } from '@/utils/date'
import { getInterationVersion } from "./project"

export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export function transferModelGroup (data: OriginModelGroup) {
  const group: ModelGroup = {
    id: data.id,
    name: data.name,
    projectId: data.project_id,
    createTime: format(data.create_datetime),
  }
  return group
}

export function transferModel (data: OriginModelVersion): ModelVersion {
  return {
    id: data.id,
    name: data.name,
    groupId: data.model_group_id,
    projectId: data.project_id,
    hash: data.hash,
    version: data.version_num || 0,
    versionName: getInterationVersion(data.version_num),
    state: data.result_state,
    map: data.map || 0,
    url: data.url || '',
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
    taskId: data.related_task.id,
    progress: data.related_task.percent || 0,
    taskType: data.related_task.type,
    taskState: data.related_task.state,
    taskName: data.related_task.name,
    task: data.related_task,
  }
}
