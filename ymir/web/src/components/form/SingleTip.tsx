import { CSSProperties, FC } from 'react'
import { Popover, PopoverProps } from 'antd'

import { TipsIcon } from '@/components/common/Icons'
import s from './tip.less'

type Props = PopoverProps & {
  iconStyles?: CSSProperties,
}

const Tip: FC<Props> = ({ title = null, content = '', placement = 'right', iconStyles = {}, ...resProps }) => {
  return (
    <Popover {...resProps} title={title} content={<div style={{ maxWidth: '20vw' }}>{content}</div>} placement={placement}>
      <TipsIcon className={s.icon} style={iconStyles} />
    </Popover>
  )
}

export default Tip
