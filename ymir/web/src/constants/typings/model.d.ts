import { Group, Result } from './common'

interface Stage {
  id: number
  name: string
  primaryMetric: number
  primaryMetricLabel?: string
  modelId?: number
  modelName?: string
  metrics?: StageMetrics
}
interface ModelGroup extends Group {
  versions?: Model[]
}
interface Model extends Result {
  map: number
  url: string
  stages?: Array<Stage>
  recommendStage: number
}
type BaseStageMetrics = {
  primary: number
  tp?: number
  fp?: number
  fn?: number
}
interface DetectionStageMetrics extends BaseStageMetrics {
  ap: number
  ar?: number
}
interface SemanticStageMetrics extends BaseStageMetrics {
  iou: number
  acc?: number
}
interface InstanceStageMetrics extends BaseStageMetrics {
  maskAP: number
  boxAP?: number
}

type StageMetrics = DetectionStageMetrics | SemanticStageMetrics | InstanceStageMetrics

export { Stage, ModelGroup, Model, StageMetrics }
