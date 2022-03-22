import { Button, Col, Row, Space } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import { states, statesLabel } from '@/constants/dataset'
import { TASKSTATES, getTaskStateLabel } from '@/constants/task'
import s from './iteration.less'

function Stage({ stage, current = 0, end = false, next = () => { }, ...func }) {
  console.log('stage: ', stage, end)

  function skip() {
    updateIteration({ skip: true, id: stage.iterationId, next: stage.next, })
  }

  function next() {
    updateIteration({ skip: false, id: stage.iterationId, next: stage.next, result: stage.result, })
  }

  async function updateIteration(params) {
    const result = await func.updateIteration(params)
    if (result) {
      next(stage)
    }
  }

  const currentStage = () => current === stage.value
  const finishStage = () => stage.value < current
  const pendingStage = () => stage.value > current

  const isPending = () => stage.state < 0
  const isReady = () => stage?.state === states.READY
  const isValid = () => stage?.state === states.VALID
  const isInvalid = () => stage?.state === states.INVALID

  const stateClass = `${s.stage} ${currentStage() ? s.current : (finishStage() ? s.finish : s.pending)}`

  const renderCount = () => {
    if (finishStage() || (currentStage() && isValid())) {
      return '√' // finish state
    } else {
      return stage.value
    }
  }
  const renderMain = () => {
    return currentStage() ? renderMainBtn() : <span>{t(stage.act)}</span>
  }

  const renderMainBtn = () => {
    // show by task state and result
    const disabled = isReady() || isInvalid()
    const label = isValid() ? '下一步' : t(stage.act)
    return <Button disabled={disabled} className={s.act} type='primary' onClick={() => next()}>{label}</Button>
  }

  const renderReactBtn = () => {
    return stage.react && currentStage()
      && (isInvalid() || isValid())
      ? <Button className={s.react}>{t(stage.react)}</Button>
      : null
  }
  const renderState = () => {
    const pending = 'project.stage.state.pending'
    const result = stage.result
    return !finishStage() ? (isPending() ? t(pending) : (result ? result : statesLabel(stage.state))) : null
  }

  const renderSkip = () => {
    return !stage.unskippable && currentStage() ? <span className={s.skip} onClick={() => skip()}>skip</span> : null
  }
  return (
    <div className={stateClass}>
      <Row className={s.row} align='middle'>
        <Col flex={"30px"}><span className={s.num}>{renderCount()}</span></Col>
        <Col>
          <Space>
            {renderMain()}
            {renderReactBtn()}
          </Space>
        </Col>
        <Col className={s.lineContainer} hidden={end} flex={1}><span className={s.line}></span></Col>
      </Row>
      <Row className={s.row}>
        <Col flex={"30px"}>&nbsp;</Col>
        <Col className={s.state} flex={1}>
          {renderState()} {renderSkip()}
        </Col>
      </Row>
    </div>
  )
}

const props = (state) => {
  return {}
}

const actions = (dispacth) => {
  return {
    updateIteration(params) {
      return dispacth({
        type: 'iteration/updateIteration',
        payload: params,
      })
    }
  }
}

export default connect(props, actions)(Stage)
