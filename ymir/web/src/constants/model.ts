import { ModelGroup, ModelVersion } from "@/interface/model"
import { calDuration, format } from '@/utils/date'
import { getIterationVersion } from "./project"
import { BackendData } from "@/interface/common"
import { getLocale } from "umi"

export enum states {
  READY = 0,
  VALID = 1,
  INVALID = 2,
}

export function transferModelGroup (data: BackendData) {
  const group: ModelGroup = {
    id: data.id,
    name: data.name,
    projectId: data.project_id,
    createTime: format(data.create_datetime),
  }
  return group
}

export function transferModel (data: BackendData): ModelVersion {
  return {
    id: data.id,
    name: data.group_name,
    groupId: data.model_group_id,
    projectId: data.project_id,
    hash: data.hash,
    version: data.version_num || 0,
    versionName: getIterationVersion(data.version_num),
    state: data.result_state,
    keywords: data?.related_task?.parameters?.keywords || [],
    map: data.map || 0,
    url: data.url || '',
    createTime: format(data.create_datetime),
    updateTime: format(data.update_datetime),
    taskId: data.related_task.id,
    progress: data.related_task.percent || 0,
    taskType: data.related_task.type,
    taskState: data.related_task.state,
    taskName: data.related_task.name,
    duration: data.related_task.duration,
    durationLabel: calDuration(data.related_task.duration, getLocale()),
    task: data.related_task,
    hidden: !data.is_visible,
  }
}
