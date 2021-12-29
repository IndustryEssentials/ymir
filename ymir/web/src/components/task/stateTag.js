import { Tag } from 'antd'
import { TASKSTATES } from '@/constants/task'
import { getTaskStates } from '@/constants/query'
import s from './stateTag.less'
import { InprogressIcon, SuccessIcon, FailIcon, StopIcon } from '@/components/common/icons'

export default function StateTag({ state, size='normal', mode='all', iconStyle = {}, label = false, ...resProps }) {
  const states = getTaskStates()
  state = state || TASKSTATES.PENDING
  const maps = {
    [TASKSTATES.PENDING]: { icon: <InprogressIcon className={s.stateIcon} style={{...iconStyle, color: '#3BA0FF'}} />, },
    [TASKSTATES.DOING]: { icon: <InprogressIcon className={s.stateIcon} style={iconStyle} />, color: 'warning' },
    [TASKSTATES.FINISH]: { icon: <SuccessIcon className={s.stateIcon} style={iconStyle} />, color: 'success' },
    [TASKSTATES.FAILURE]: { icon: <FailIcon className={s.stateIcon} style={iconStyle} />, color: 'error' },
    [TASKSTATES.TERMINATED]: { icon: <StopIcon className={s.stateIcon} style={{iconStyle, color: 'rgba(0, 0, 0, 0.65)'}} />, },
  }
  const target = states.find(s => s.value === state)
  return (
    <Tag
      className={`${s.state} ${s[mode]} ${s[size]}`}
      {...resProps}
      color={maps[target.value].color}
      title={target.label}
    >
      {maps[target.value].icon}
      {mode !== 'icon' ? target.label : ''}
    </Tag>
  )
}