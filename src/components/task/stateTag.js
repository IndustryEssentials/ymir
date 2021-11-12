import { Tag } from 'antd'
import { TASKSTATES } from '@/constants/task'
import { getTaskStates } from '@/constants/query'
import { InprogressIcon, SuccessIcon, FailIcon, } from '@/components/common/icons'

export default function StateTag({ state, iconstyle = {}, label = false, ...resProps }) {
  const states = getTaskStates()
  state = state || TASKSTATES.PENDING
  const iconStyle = { marginRight: 5, fontSize: 14, ...iconstyle }
  const noLabelStyle = { border: 'none', background: 'none', margin: 0, padding: 0 }
  const maps = {
    [TASKSTATES.PENDING]: { icon: <InprogressIcon style={{...iconStyle, color: '#3BA0FF'}} />, },
    [TASKSTATES.DOING]: { icon: <InprogressIcon style={iconStyle} />, color: 'warning' },
    [TASKSTATES.FINISH]: { icon: <SuccessIcon style={iconStyle} />, color: 'success' },
    [TASKSTATES.FAILURE]: { icon: <FailIcon style={iconStyle} />, color: 'error' },
  }
  const target = states.find(s => s.value === state)
  return (
    <Tag
      style={label ? null : noLabelStyle}
      {...resProps}
      color={maps[target.value].color}
      title={target.label}
    >
      {maps[target.value].icon}
      {label ? target.label : ''}
    </Tag>
  )
}