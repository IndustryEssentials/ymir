import { percent } from '@/utils/number'
import { Popover } from 'antd'
import ReactJson from 'react-json-view'

export function getModelCell(rid, tasks, models) {
  const task = tasks.find(({ result }) => result === rid)
  const model = models.find(model => model.id === task.model)
  const stage = model.stages.find(sg => sg.id === task.stage)
  const content = <ReactJson src={task.config} name={false} />
  const label = `${model.name} ${model.versionName} ${stage.name}`
  return <Popover content={content}>
    <span title={label}>{label}</span>
  </Popover>
}


export function getCK(data, keyword) {
  const cks = Object.values(data).map(({ iou_averaged_evaluation }) => {
    const ck = iou_averaged_evaluation.ck_evaluations[keyword] || {}
    return ck.sub ? Object.keys(ck.sub) : []
  }).flat()
  const uniqueCKs = [...new Set(cks)]
  return uniqueCKs.map(k => ({ value: k, label: k, parent: keyword }))
}

export const opt = d => ({ value: d.id, label: `${d.name} ${d.versionName}`, })

export const average = (nums = []) => nums.reduce((prev, num) => !Number.isNaN(num) ? prev + num : prev, 0) / nums.length

export const getKwField = ({ iou_evaluations, iou_averaged_evaluation }, type) => !type ?
  Object.values(iou_evaluations)[0]['ci_evaluations'] :
  iou_averaged_evaluation['ck_evaluations']

export const percentRender = value => typeof value === 'number' && !Number.isNaN(value) ? percent(value) : '-'
