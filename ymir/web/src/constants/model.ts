import { OriginModelGroup, ModelGroup, OriginModelVersion, ModelVersion } from "@/interface/model"
import { format } from '@/utils/date'

export enum states {
  READY = 1,
  VALID = 2,
  INVALID = 3,
}

export function transferModelGroup (data: OriginModelGroup) {
  const group: ModelGroup = {
    ...data,
    createTime: format(data.create_datetime),
  }
  return group
}

export function transferModelVersion (data: OriginModelVersion): ModelVersion {
  return {
    id: data.id,
    name: data.name,
    version: data.version,
    keywords: data.keywords,
    state: data.state,
    createTime: format(data.create_datetime),
    assetCount: data.asset_count,
    taskId: data.task_id,
    progress: data.progress,
    taskState: data.taskState,
  }
}
