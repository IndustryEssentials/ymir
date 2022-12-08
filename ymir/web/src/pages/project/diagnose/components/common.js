import { percent, toFixed } from '@/utils/number'
import { Popover } from 'antd'
import ReactJson from 'react-json-view'

export function getModelCell(rid, tasks, models, text) {
  const task = tasks.find(({ result }) => result === rid)
  const model = models.find((model) => model.id === task.model)
  const stage = model.stages.find((sg) => sg.id === task.stage)
  const content = <ReactJson src={task.config} name={false} />
  const label = `${model.name} ${model.versionName} ${stage.name} ${task.configName}`
  return text ? (
    label
  ) : (
    <Popover content={content}>
      <span title={label}>{label}</span>
    </Popover>
  )
}

export function getCK(data, keyword) {
  const cks = Object.values(data)
    .map(({ iou_averaged_evaluation }) => {
      const ck = iou_averaged_evaluation.ck_evaluations[keyword] || {}
      return ck.sub ? Object.keys(ck.sub) : []
    })
    .flat()
  const uniqueCKs = [...new Set(cks)]
  return uniqueCKs.map((k) => ({ value: k, label: k, parent: keyword }))
}

export const opt = (d) => ({ value: d.id, label: `${d.name} ${d.versionName}` })

export const average = (nums = []) => nums.reduce((prev, num) => (!Number.isNaN(num) ? prev + num : prev), 0) / nums.length

export const getKwField = (evaluation = {}, type) => {
  const data = evaluation || {}
  const ev = data[!type ? 'dataset_evaluation' : 'sub_cks'] || {}
  if (type) {
    // ck
    return Object.keys(ev).reduce((prev, curr) => {
      const ap = ev[curr]?.iou_averaged_evaluation?.ci_averaged_evaluation || {}
      return {
        ...prev,
        [curr]: ap,
      }
    }, {})
  } else {
    const result = Object.values(ev.iou_evaluations || {})[0] || {}
    return result?.ci_evaluations || {}
  }
}

export const getAverageField = (evaluation) => {
  const data = evaluation || {}
  return data?.dataset_evaluation?.iou_averaged_evaluation?.ci_evaluations || {}
}

export const percentRender = (value) => (typeof value === 'number' && !Number.isNaN(value) ? percent(value) : '-')

export const confidenceRender = (value) => (typeof value === 'number' && !Number.isNaN(value) ? toFixed(value, 3) : '-')
