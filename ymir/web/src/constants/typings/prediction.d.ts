import { TASKTYPES } from '../task'
import { Classes } from './class'
import { AnnotationsCount, Dataset } from './dataset'
import { ImageConfig } from './image'
import { Model } from './model'
import { ParamsByType } from './task'

interface Prediction extends Omit<Dataset, 'suggestions' | 'task'> {
  inferModelId: number[]
  inferModel?: Model
  inferDatasetId: number
  inferDataset?: Dataset
  inferConfig: ImageConfig
  rowSpan?: number
  evaluated: boolean
  pred: AnnotationsCount
  inferClass?: Classes
  odd?: boolean
  task: ParamsByType[TASKTYPES.INFERENCE]
}

export { Prediction }
