
export interface DatasetGroup {
  id: number,
  name: string,
  projectId: number,
  createTime: string,
}

export interface DatasetVersion {
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
  taskId: number,
  progress: number,
  taskState: number,
  taskType: number,
  ignoredKeywords: Array<string>,
  hash: string,
}


export interface OriginDatasetGroup {
  id: number,
  name: string,
  project_id: number,
  create_datetime: string,
}

export interface OriginDatasetVersion {
  version: number;
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
  progress: number,
  result_state: number,
  ignored_keywords: Array<string>,
  create_datetime: string,
  update_datetime: string,
  task_id: number,
  related_task: Task,
}

interface Task {
  name: string,
  type: number,
  project_id: number,
  is_deleted: number,
  create_datetime: string,
  update_datetime: string,
  id: number,
  hash: string,
  state: number,
  error_code: number,
  duration: number,
  percent: number,
  parameters: object,
  config: object,
  result_type: number,
}
