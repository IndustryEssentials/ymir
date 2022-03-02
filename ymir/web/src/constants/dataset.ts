import { OriginDatasetGroup, DatasetGroup, OriginDatasetVersion, DatasetVersion } from "@/interface/dataset"
import { format } from '@/utils/date'

export enum states {
  READY = 1,
  VALID = 2,
  INVALID = 3,
}

export function transferDatasetGroup (data: OriginDatasetGroup) {
  const group: DatasetGroup = {
    ...data,
    createTime: format(data.create_datetime),
  }
  return group
}

export function transferDatasetVersion (data: OriginDatasetVersion): DatasetVersion {
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
