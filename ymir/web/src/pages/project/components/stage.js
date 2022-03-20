import { Button, Col, Row, Space } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import { states } from '@/constants/dataset'
import s from './iteration.less'

const stageStates = {
  [states.READY]: 'project.stage.state.ready',
  [states.VALID]: 'project.stage.state.valid',
  [states.INVALID]: 'project.stage.state.invalid',
}

function Stage({ stage, end = false }) {
  console.log('stage: ', stage, end)
  
  function skip() {}
  return (
    <div className={s.stage}>
      <Row className={s.row} align='middle'>
        <Col flex={"30px"}><span className={s.num}>{stage.id}</span></Col>
        <Col>
          <Space>
            <Button className={s.act} type='primary'>{t(stage.act)}</Button> 
            {stage.react ? <Button className={s.react}>{t(stage.react)}</Button> : null }
          </Space>
        </Col>
        <Col className={s.lineContainer} hidden={end} flex={1}><span className={s.line}></span></Col>
      </Row>
      <Row className={s.row}>
        <Col flex={"30px"}>&nbsp;</Col>
        <Col className={s.state} flex={1}>
          state, <span className={s.skip} onClick={() => skip()}>skip</span>
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
