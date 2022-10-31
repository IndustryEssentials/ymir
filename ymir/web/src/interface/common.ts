import { Project } from "./project"
import { Task } from "./task"

export type BackendData = {
  [key: string]: any,
}

export interface Group {
  id: number,
  name: string,
  projectId: number,
  createTime: string,
}

export interface Result {
  id: number,
  groupId: number,
  projectId: number,
  name: string,
  versionName: string,
  version: number,
  keywords: Array<string>,
  isProtected?: Boolean,
  state: number,
  createTime: string,
  updateTime: string,
  hash: string,
  taskId: number,
  progress: number,
  taskState: number,
  taskType: number,
  duration: number,
  durationLabel?: string,
  taskName: string,
  project?: Project,
  task?: Task,
  hidden: boolean,
  description: string,
}
