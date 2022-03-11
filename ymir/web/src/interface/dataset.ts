
import { Project } from './project'
import { Task } from './task'
export interface DatasetGroup {
  id: number,
  name: string,
  projectId: number,
  createTime: string,
}

export interface Dataset {
  id: number,
  groupId: number,
  projectId: number,
  name: string,
  versionName: string,
  version: number,
  keywords: Array<string>,
  keywordCount: number,
  state: number,
  createTime: string,
  updateTime: string,
  assetCount: number,
  ignoredKeywords: Array<string>,
  hash: string,
  taskId: number,
  progress: number,
  taskState: number,
  taskType: number,
  duration: number,
  taskName: string,
  project?: Project,
  task?: Task,
}


export interface OriginDatasetGroup {
  id: number,
  name: string,
  project_id: number,
  create_datetime: string,
}

export interface OriginDataset {
  id: number,
  dataset_group_id: number,
  project_id: number,
  hash: string,
  name: string,
  version_num: number,
  keywords: Array<string>,
  state: number,
  asset_count: number,
  keyword_count: number,
  result_state: number,
  ignored_keywords: Array<string>,
  create_datetime: string,
  update_datetime: string,
  task_id: number,
  related_task: Task,
}
