import { Task } from "./task";

export interface ModelGroup {
  id: number,
  projectId: number,
  name: string,
  createTime: string,
}

export interface ModelVersion {
  id: number,
  groupId: number,
  projectId: number,
  name: string,
  hash: string,
  version: number,
  versionName: string,
  state: number,
  map: number,
  url: string,
  createTime: string,
  updateTime: string,
  taskId: number,
  progress: number,
  taskType: number,
  taskState: number,
  taskName: string,
}


export interface OriginModelGroup {
  id: number,
  name: string,
  project_id: number,
  create_datetime: string,
}

export interface OriginModelVersion {
  version: number;
  keywords: any;
  state: number;
  id: number,
  model_group_id: number,
  project_id: number,
  name: string,
  version_num: number,
  task_id: number,
  hash: string,
  map: number,
  result_state: number,
  url: string,
  related_task: Task,
  create_datetime: string,
  update_datetime: string,
}
