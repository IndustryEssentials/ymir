import { percent, toFixed } from '@/utils/number'
import { Popover } from 'antd'
import ReactJson from 'react-json-view'

export type Task = {
  config: { [key: string]: string | number }
  configName: string
  testing: number
  model: number
  stage: number
  result: number
}
export type MetricType = {
  map: number
  pr_curve?: [x: number, y: number, z: number][]
}

type CIType = {
        ci_averaged_evaluation: {
          [key: string]: MetricType
        }
        ci_evaluations: {
          [key: string]: MetricType
        }
}
export type IOUDataType = {
      iou_averaged_evaluation: CIType
      iou_evaluations: CIType
}
export type DataType = {
  dataset_evaluation: IOUDataType
  sub_cks?: {
    [key: string]: IOUDataType
  }
}

export function getModelCell(rid: number, tasks: Task[], models: YModels.Model[], text: string) {
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

export const getAverageField = (evaluation: DataType) => {
  const data = evaluation || {}
  return data?.dataset_evaluation?.iou_averaged_evaluation?.ci_evaluations || {}
}

export const percentRender = (value: string | number) => (typeof value === 'number' && !Number.isNaN(value) ? percent(value) : '-')

export const confidenceRender = (value: string | number) => (typeof value === 'number' && !Number.isNaN(value) ? toFixed(value, 3) : '-')
