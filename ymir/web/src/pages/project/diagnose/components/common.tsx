import { percent, toFixed } from '@/utils/number'
import { attr2LowerCase } from '@/utils/object'
import { Popover } from 'antd'
import ReactJson from 'react-json-view'

export type TabIdType = 'ap' | 'iou' | 'acc' | 'maskap' | 'boxap' | 'curve' | 'rp' | 'pr'
type MetricKeys = Exclude<TabIdType, 'rp' | 'pr' | 'curve'> | 'pr_curve'
export type Task = {
  config: { [key: string]: string | number }
  configName: string
  testing: number
  model: number
  stage: number
  result: number
}

export type ViewProps = {
  type: MetricKeys
  tasks: Task[]
  datasets: YModels.Dataset[]
  models: YModels.Model[]
  data: YModels.BackendData
  p2r?: boolean
  prRate?: number[]
  xByClasses?: boolean
  kw: { ck?: boolean; keywords: string[] }
  averageIou?: number
}
export type MetricType = {
  ap?: number
  pr_curve?: [x: number, y: number, z: number][]
  iou?: number
  acc?: number
  maskap?: number
  boxap?: number
}

export type MetricsType = {
  [key: string]: MetricType
}

type CIType = {
  ci_averaged_evaluation: MetricsType
  ci_evaluations: MetricsType
}
export type IOUDataType = {
  iou_averaged_evaluation: CIType
  iou_evaluations: { [iou: string]: CIType }
  segmentation_metrics: {
    [metric: string]: { [keyword: string]: number }
  }
}
export type DataType = {
  dataset_evaluation: IOUDataType
  sub_cks?: {
    [key: string]: IOUDataType
  }
}

export function getModelCell(rid: number, tasks: Task[], models: YModels.Model[], text?: string) {
  const task = tasks.find(({ result }) => result === rid)
  const model = models.find((model) => model.id === task?.model)
  const stage = model?.stages?.find((sg) => sg.id === task?.stage)
  if (!task || !model || !stage) {
    return
  }
  const content = <ReactJson src={task?.config} name={false} />
  const label = `${model.name} ${model.versionName} ${stage.name} ${task.configName}`
  return text ? (
    label
  ) : (
    <Popover content={content}>
      <span title={label}>{label}</span>
    </Popover>
  )
}

export function getCK(data: { iou_averaged_evaluation: { ck_evaluations: { [key: string]: { sub: { [key: string]: number } } } } }[], keyword: string) {
  const cks = Object.values(data)
    .map(({ iou_averaged_evaluation }) => {
      const ck = iou_averaged_evaluation.ck_evaluations[keyword] || {}
      return ck.sub ? Object.keys(ck.sub) : []
    })
    .flat()
  const uniqueCKs = [...new Set(cks)]
  return uniqueCKs.map((k) => ({ value: k, label: k, parent: keyword }))
}

export const opt = (d: YModels.Result) => ({ value: d.id, label: `${d.name} ${d.versionName}` })

export const average = (nums = []) => nums.reduce((prev, num) => (!Number.isNaN(num) ? prev + num : prev), 0) / nums.length

export const getKwField = (evaluation: DataType, type: boolean) => {
  const data = evaluation || {}
  if (type) {
    // ck
    const data = evaluation?.sub_cks || {}
    return Object.keys(data).reduce((prev, curr) => {
      const ap = data[curr] ? data[curr]?.iou_averaged_evaluation?.ci_averaged_evaluation : {}
      return {
        ...prev,
        [curr]: ap,
      }
    }, {})
  } else {
    const result = Object.values(data.dataset_evaluation.iou_evaluations || {})[0] || {}
    return result?.ci_evaluations || {}
  }
}

const lowerMetrics = (metrics: { [key: string]: { [metric: string]: any } }): MetricsType => {
  return Object.keys(metrics).reduce((prev, key) => {
    const ap = metrics[key]
    return {
      ...prev,
      [key]: attr2LowerCase(ap),
    }
  }, {})
}

const getRowDataByCK = (result?: DataType): { [keyword: string]: MetricType } => {
  const data = result?.sub_cks || {}
  return data
    ? Object.keys(data).reduce((prev, curr) => {
        const ap = data[curr] ? data[curr]?.iou_averaged_evaluation?.ci_averaged_evaluation : {}
        return {
          ...prev,
          [curr]: attr2LowerCase(ap),
        }
      }, {})
    : {}
}

export const getDetRowforDataset = (evaluation: DataType, isCk?: boolean) => {
  return isCk ? getRowDataByCK(evaluation) : getDetectionRowData(evaluation)
}

export const getSegRowforDataset = (evaluation: DataType, field: string) => {
  return getSegmentationRowData(evaluation, field)
}
const getDetectionRowData = (result?: DataType): { [keyword: string]: MetricType } => {
  const data = Object.values(result?.dataset_evaluation?.iou_evaluations || {})[0] || {}
  const evaluation = data?.ci_evaluations || {}
  return Object.keys(evaluation).reduce((prev, key) => {
    const metrics = evaluation[key]
    const lower = attr2LowerCase(metrics)
    return {
      ...prev,
      [key]: lower,
    }
  }, {})
}

const getSegmentationRowData = (result: DataType, field: string): { [keyword: string]: MetricType } => {
  const metrics = attr2LowerCase(result?.dataset_evaluation?.segmentation_metrics || {})
  const data = metrics[field] || {}
  return Object.keys(data).reduce((prev, keyword) => {
    return {
      ...prev,
      [keyword]: {
        [field]: data[keyword],
      },
    }
  }, {})
}

export const getAverageField = (evaluation: DataType) => {
  const data = evaluation || {}
  return lowerMetrics(data?.dataset_evaluation?.iou_averaged_evaluation?.ci_evaluations || {})
}

export const percentRender = (value: string | number) => (typeof value === 'number' && !Number.isNaN(value) ? percent(value) : '-')

export const confidenceRender = (value: string | number) => (typeof value === 'number' && !Number.isNaN(value) ? toFixed(value, 3) : '-')
