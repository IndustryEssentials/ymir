import { Col, Popover, Row } from "antd"

import { TipsIcon } from '@/components/common/icons'
import s from './tip.less'

const Tip = ({ title = null, content = '', placement = 'right', span=6, hidden = false, children }) => {
  const tip = <Popover title={title} content={<div style={{ maxWidth: '20vw' }}>{content}</div>} placement={placement}>
    <TipsIcon className={s.icon} />
  </Popover>
  return (
    <Row gutter={10}>
      <Col flex={1}>{children}</Col>
      <Col span={span}>{hidden ? null : tip}</Col>
    </Row>
  )
}

export default Tip
