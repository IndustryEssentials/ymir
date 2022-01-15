import { Popover } from "antd"

import { TipsIcon } from '@/components/common/icons'
import s from './tip.less'

const Tip = ({ title = null, content = '', placement = 'right', ...resProps }) => {
  return <Popover title={title} content={<div style={{ maxWidth: '20vw' }}>{content}</div>} placement={placement}>
    <TipsIcon className={s.icon} {...resProps} />
  </Popover>
}

export default Tip
