import { Row, Col } from "antd"
import { connect } from "dva"

import s from "./iteration.less"

function Iteration({}) {
  const Num = ({ num, state }) => {
    return <div>{num}</div>
  }
  const iterationStages = [
    { id: 1, step: 1, state: 1 },
    { id: 2, step: 2, state: 2 },
    { id: 3, step: 3, state: 3 },
    { id: 4, step: 4, state: 4 },
    { id: 5, step: 5, state: 5 },
    { id: 6, step: 6, state: 6 },
  ]
  return (
    <div className={s.iteration} hidden={true}>
      <Row>
        {iterationStages.map((stage) => (
          <Col flex={1}>
            <Stage />
          </Col>
        ))}
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

export default connect(props, actions)(Iteration)
