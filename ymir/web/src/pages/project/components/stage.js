import { Button, Col, Row } from "antd"
import { connect } from "dva"

function Stage({}) {
  return (
    <div className={s.stage}>
    <Row>
      <Col flex={'80px'}>1</Col>
      <Col>
        <Space>
          <Button>step</Button> <Button>reAct</Button>
        </Space>
      </Col>
      <Col flex={1}>line</Col>
    </Row>
    <Row>
      <Col flex={'80px'}>&nbsp;</Col>
      <Col flex={1}>
        state, <span onClick={}>skip</span>
      </Col>
    </Row>
    </div>
  )
}

const props = (state) => {
  return {}
}

const actions = (dispacth) => {
  return {}
}

export default connect(props, actions)(Stage)
