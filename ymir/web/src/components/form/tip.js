import { Col, Row } from "antd"

import SingleTip from './singleTip'

const Tip = ({ title = null, content = '', placement = 'right', span=6, formSpan=0, hidden = false, children }) => {
  return (
    <Row gutter={10} wrap={false}>
      <Col span={formSpan || (24 - span)}>{children}</Col>
      <Col span={span}>{hidden ? null : <SingleTip title={title} content={content} placement={placement} style={{ lineHeight: '40px' }} />}</Col>
    </Row>
  )
}

export default Tip
