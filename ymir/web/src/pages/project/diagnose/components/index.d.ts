import { ReactElement } from 'react'

type TabIdType = 'ap' | 'iou' | 'acc' | 'maskap' | 'boxap' | 'curve' | 'rp' | 'pr'
type MetricKeys = Exclude<TabIdType, 'rp' | 'pr' | 'curve'> | 'pr_curve'
type Point = {
  x: number
  y: number
  z: number
}

type OptionType<ValueType = string> = {
  value: ValueType
  label: string
}

type Task = {
  config: { [key: string]: string | number }
  configName: string
  testing: number
  model: number
  stage: number
  result: number
}

type ViewProps = {
  type: TabIdType
  predictions: YModels.Prediction[]
  datasets: YModels.Dataset[]
  models: YModels.Model[]
  data?: EvaluationResult
  p2r?: boolean
  prRate?: number[]
  xByClasses?: boolean
  kw: { ck?: boolean; keywords: string[] }
  averageIou?: boolean
}
type MetricType  = { [key: string]: any } & {
  ap?: number
  pr_curve?: Point[]
  iou?: number
  acc?: number
  maskap?: number
  boxap?: number
}

type MetricsType = {
  [key: string | number]: MetricType
}

type CIType = {
  ci_averaged_evaluation: MetricsType
  ci_evaluations: MetricsType
}
type IOUDataType = {
  iou_averaged_evaluation: CIType
  iou_evaluations: { [iou: string]: CIType }
  segmentation_metrics: {
    [metric: string]: { [keyword: string]: number }
  }
}
type DataType = {
  dataset_evaluation: IOUDataType
  sub_cks?: {
    [key: string]: IOUDataType
  }
}

type EvaluationResult = {
  [key: string | number]: DataType
}

type TableDataType = {
  id: string | number
  value: string | number
  name?: string | ReactElement
  a?: number
  ca?: number
}

type ChartDataType = {
  id: string | number
  lines: LineType[]
  title?: string
}
type LineType = {
  id: string | number
  name?: string | ReactElement
  line?: Point[]
}

type DataTypeForTable = {
  [key: string | number]: MetricsType
}


type ListType<RowDataType = TableDataType> = {
  id: string | number
  label: string
  rows: RowDataType[]
}[]

export {
  EvaluationResult,
  DataType,
  IOUDataType,
  MetricsType,
  MetricType,
  MetricKeys,
  Task,
  ViewProps,
  Point,
  TabIdType,
  OptionType,
  TableDataType,
  ChartDataType,
  DataTypeForTable,
  ListType,
}
