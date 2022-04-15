import { Tag } from 'antd'
import { STATES, getUserState } from '@/constants/user'
import t from '@/utils/t'
import s from './stateTag.less'
import { SuccessIcon, FailIcon, ShutIcon, TipsIcon } from '../common/icons'

export default function StateTag({ state }) {
  const maps = {
    [STATES.REGISTERED]: { icon: <TipsIcon className={s.stateIcon} />, color: 'warning' },
    [STATES.ACTIVE]: { icon: <SuccessIcon className={s.stateIcon} />, color: 'success' },
    [STATES.DECLINED]: { icon: <FailIcon className={s.stateIcon} />, color: 'error' },
    [STATES.DEACTIVED]: { icon: <ShutIcon className={s.stateIcon} style={{ color: 'rgba(0, 0, 0, 0.25)'}} /> },
  }
  const target = { ...maps[state], label: t(getUserState(state)) }
  return (
    <Tag
      className={s.state}
      color={target.color}
      title={target.label}
    >
      {target.icon}
      {target.label}
    </Tag>
  )
}