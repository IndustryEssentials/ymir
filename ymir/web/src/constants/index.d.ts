import { ResultStates } from './common'
import { Asset, AnnotationBase, Annotation, SegAnnotation, DetAnnotation, BoundingBox, Polygon, Mask } from './typings/asset.d'
import { Classes, ClassObject, ClassesCount, CustomClass } from './typings/class.d'
import { Backend, Matable, Result, Group } from './typings/common.d'
import {
  DatasetGroup,
  Dataset,
  Suggestion,
  DatasetSuggestions,
  AnnotationsCount,
  DatasetAnalysis,
  KeywordCountsType,
  AnalysisChartData,
  AnalysisChart,
  CKItem,
} from './typings/dataset.d'
import { Image, ImageConfig, DockerImageConfig } from './typings/image.d'
import { Message, MessageResultModules } from './typings/message.d'
import { Model, ModelGroup, Stage, StageMetrics } from './typings/model.d'
import { Prediction } from './typings/prediction.d'
import { Project } from './typings/project.d'
import { SysInfo } from './typings/sysinfo.d'
import { Task, ProgressTask } from './typings/task.d'
import { Iteration, Step } from './typings/iteration.d'
import { Queue, QueueItem } from './typings/queue.d'
import { User } from './typings/user.d'

type UserLogRecord = {
  id: number
  action: number
  state: number
  content: string
  actionLabel: string
  // relatedEntity: {}
  time: string
  task?: Task
}

export {
  Asset,
  AnnotationBase,
  Annotation,
  SegAnnotation,
  DetAnnotation,
  BoundingBox,
  Polygon,
  Mask,
  Message,
  MessageResultModules,
  Prediction,
  Image,
  ImageConfig,
  DockerImageConfig,
  Task,
  SysInfo,
  Backend,
  Classes,
  ClassObject,
  ClassesCount,
  CustomClass,
  Matable,
  Dataset,
  DatasetGroup,
  Suggestion,
  AnnotationsCount,
  DatasetSuggestions,
  DatasetAnalysis,
  KeywordCountsType,
  AnalysisChartData,
  AnalysisChart,
  CKItem,
  Result,
  Group,
  Model,
  ModelGroup,
  Stage,
  StageMetrics,
  Project,
  ProgressTask,
  Iteration,
  Step,
  UserLogRecord,
  Queue,
  QueueItem,
  User,
}
