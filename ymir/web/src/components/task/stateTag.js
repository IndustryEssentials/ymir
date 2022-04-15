import { Tag } from 'antd'
import t from '@/utils/t'
import { states, statesLabel } from '@/constants/dataset'
import s from './stateTag.less'
import { InprogressIcon, SuccessIcon, FailIcon, } from '@/components/common/icons'

export default function StateTag({ state = states.READY, size='normal', mode='all', iconStyle = {}, ...resProps }) {
  const maps = {
    [states.READY]: { icon: <InprogressIcon className={s.stateIcon} style={{...iconStyle, color: '#3BA0FF'}} />, },
    [states.VALID]: { icon: <SuccessIcon className={s.stateIcon} style={iconStyle} />, color: 'success' },
    [states.INVALID]: { icon: <FailIcon className={s.stateIcon} style={iconStyle} />, color: 'error' },
  }
  const label = t(statesLabel(state))
  const tag = maps[state]
  return tag ? (
    <Tag
      className={`${s.state} ${s[mode]} ${s[size]}`}
      {...resProps}
      color={tag.color}
      title={label}
    >
      {tag.icon}
      {mode !== 'icon' ? label : ''}
    </Tag>
  ) : null
}