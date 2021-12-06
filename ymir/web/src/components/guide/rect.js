import { Col, Row } from "antd"
import s from './guide.less'


const Rect = ({x = 0, y = 0, width = 0, height = 0, visible = false }) => {

  return (
    <div className={s.rect} hidden={!visible}>
      <div className={s.header} style={{ height: y }}></div>
      <Row className={s.content}>
        <Col className={s.left} style={{ width: x}}></Col>
        <Col className={s.center} style={{ width, height }}></Col>
        <Col className={s.right} flex={1}></Col>
      </Row>
      <div className={s.footer}></div>
    </div>
  )
}

export default Rect
