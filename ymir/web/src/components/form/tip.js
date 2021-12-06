import { Popover } from "antd"

import { TipsIcon } from '@/components/common/icons'
import s from './tip.less'

const Tip = ({ title = null, content = '', placement = 'right'}) => {

  return (
    <Popover title={title} content={content} placement={placement}>
      <TipsIcon className={s.icon} />
    </Popover>
  )
}

export default Tip
