import t from '@/utils/t'
import React from 'react'
import { STATES as states } from '@/constants/image'
import { LoadingOutlined } from '@ant-design/icons'
import { SuccessIcon, FailIcon } from '@/components/common/Icons'

type Props = {
  state?: states
  label?: boolean
}

const StateTag: React.FC<Props> = ({ state = states.PENDING, label }) => {
    const stateMaps = {
      [states.PENDING]: { key: 'pending', icon: <LoadingOutlined style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} /> },
      [states.DONE]: { key: 'done', icon: <SuccessIcon style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} /> },
      [states.ERROR]: { key: 'error', icon: <FailIcon style={{ color: 'rgba(242, 99, 123, 1)', fontSize: 16 }} /> },
    }
    const tag = stateMaps[state]
    return <span>{tag.icon}{label ? t(`image.state.${tag.key}`) : null}</span>
}

export default StateTag
