import React from 'react'
import { FailIcon, TipsIcon } from '@/components/common/Icons'
import { WarningFilled } from '@ant-design/icons'
import s from './tip.less'

type Type = 'success' | 'error' | 'warning'
type Props = {
  type: Type,
  content: string | React.Component<any>
}
const types = {
  'success': TipsIcon,
  'error': FailIcon,
  'warning': WarningFilled
}
const Tip: React.FC<Props> = ({ type = 'success', content = '' }) => {
  const Icon = getIcon(type)
  return content ? (
    <div className={`${s.tipContainer} ${s[type]}`}>
      <Icon />
      {content}
    </div>
  ) : null
}

function getIcon(type: Type) {
  const cls = `${s.icon} ${s[type]}`
  const Icon = types[type]
  const I: React.FC<{[key: string]: any}> = (props) => <Icon {...props} className={cls} />
  return I
}

export default Tip
