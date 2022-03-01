import { Row, Col } from 'antd'
import { connect } from 'dva'

import s from './interation.less'

function Interation ({}) {
  const Num = ({ num, state }) => {
    return <div>{num}</div>
  }
  return <div className={s.interation} hidden={true}>    
    <Row>
      <Col flex={1}>
        <Num num={1} state={1}>1</Num>
      </Col>
    </Row>
  </div>
}

const props = state => {
  return {

  }
}

const actions = dispacth => {
  return {

  }
}

export default connect(props, actions)(Interation)