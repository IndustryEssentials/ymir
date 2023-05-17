import t from '@/utils/t'
import React from 'react'
import { STATES as states } from '@/constants/image'
import { LoadingOutlined } from '@ant-design/icons'
import { SuccessIcon, FailIcon } from '@/components/common/Icons'
import { getErrorCodeDocLink } from '@/constants/common'

type Props = {
  state?: states
  label?: boolean
  code?: string
}

const StateTag: React.FC<Props> = ({ state = states.PENDING, label, code }) => {
  const stateMaps = {
    [states.PENDING]: { key: 'pending', icon: <LoadingOutlined style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} /> },
    [states.DONE]: { key: 'done', icon: <SuccessIcon style={{ color: 'rgba(54, 203, 203, 1)', fontSize: 16 }} /> },
    [states.ERROR]: { key: 'error', icon: <FailIcon style={{ color: 'rgba(242, 99, 123, 1)', fontSize: 16 }} /> },
  }
  const tag = stateMaps[state]
  const text = (
    <span>
      {tag.icon}
      {label ? t(`image.state.${tag.key}`) : null}
    </span>
  )
  return tag.key === 'error' ? (
    <a href={getErrorCodeDocLink(code)} target="_blank" title={t(`error${code}`)}>
      {text}
    </a>
  ) : (
    text
  )
}

export default StateTag
