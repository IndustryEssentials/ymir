import { Popover } from 'antd'

import { TipsIcon } from '@/components/common/Icons'
import s from './tip.less'

const Tip = ({ title = null, content = '', placement = 'right', iconStyles = {}, ...resProps }) => {
  return (
    <Popover {...resProps} title={title} content={<div style={{ maxWidth: '20vw' }}>{content}</div>} placement={placement}>
      <TipsIcon className={s.icon} style={iconStyles} />
    </Popover>
  )
}

export default Tip
