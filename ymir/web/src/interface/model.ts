import { Project } from "./project";
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
  duration?: number,
  durationLabel?: string,
  project?: Project,
  task?: Task,
}
