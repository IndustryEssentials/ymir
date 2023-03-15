import { percent, toFixed } from '@/utils/number'
import { attr2LowerCase } from '@/utils/object'
import { Popover } from 'antd'
import ReactJson from 'react-json-view'
import { DataType, MetricsType, MetricType } from '.'

export function getModelCell(prediction: YModels.Prediction, models: YModels.Model[], text?: string) {
  const [mid, sid] = prediction?.inferModelId || []
  const model = models.find(({ id }) => mid === id)
  const stage = model?.stages?.find(({ id }) => sid === id)
  if (!prediction || !model || !stage) {
    return
  }
  const content = <ReactJson src={prediction.task?.config} name={false} />
  const label = `${model.name} ${model.versionName} ${stage.name}`
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

export const average = (nums: number[] = []) => nums.reduce((prev, num) => (!Number.isNaN(num) ? prev + num : prev), 0) / nums.length

export const getKwField = (evaluation: DataType, ck?: boolean): MetricsType => {
  const data = evaluation || {}
  if (ck) {
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
