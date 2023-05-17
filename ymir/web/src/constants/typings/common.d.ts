import { ObjectType } from '../objectType'
import { Classes } from './class'
import { Project } from './project'
import { Task } from './task'

interface Group {
  id: number
  name: string
  projectId: number
  createTime: string
}

interface Result {
  id: number
  groupId: number
  projectId: number
  type: ObjectType
  name: string
  versionName: string
  version: number
  keywords: Classes
  isProtected?: Boolean
  state: number
  createTime: string
  updateTime: string
  hash: string
  task: Task
  taskId: number
  progress: number
  taskState: number
  taskType: number
  duration: number
  durationLabel?: string
  taskName: string
  project?: Project
  hidden: boolean
  description: string
  needReload?: boolean
  groupName?: string
}

type Backend = {
  [key: string]: any
}

type Matable<U> = {
  [Type in keyof U]: {
    type: Type
  } & U[Type]
}[keyof U]

export { Backend, Matable, Result, Group }
