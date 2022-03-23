import { Button, Col, Row, Space } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import { states, statesLabel } from '@/constants/dataset'
import { TASKSTATES, getTaskStateLabel } from '@/constants/task'
import s from './iteration.less'

function Stage({ stage, current = 0, end = false, callback = () => { }, ...func }) {
  console.log('stage: ', stage, end)

  function skip() {
    func.updateIteration({ id: stage.iterationId, next: stage.next, })
  }

  function next() {
    if (isPending()) {
      if (stage.url) {
        history.push(stage.url)
      } else {
        // todo create new one
        createIteration({ round: current + 1 })
        callback()
      }
    } else if (stage.next) {
      // goto next stage
      updateIteration({ id: stage.iterationId, next: stage.next, result: stage.result, })
      callback()
    }
  }

  async function updateIteration(params) {
    const result = await func.updateIteration(params)
    if (result) {
      next({ stage })
    }
  }

  async function createIteration(params) {
    const result = await func.createIteration(params)
    if (result) {
      next({ iterationId: result.id })
    }
  }

  const currentStage = () => stage.value === stage.current
  const finishStage = () => stage.value < stage.current
  const pendingStage = () => stage.value > stage.current

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
    const label = isValid() ? t('common.step.next') : t(stage.act)
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
    return !stage.unskippable && !end && currentStage() ? <span className={s.skip} onClick={() => skip()}>skip</span> : null
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
    },
    createIteration(params) {
      return dispacth({
        type: 'iteration/createIteration',
        payload: params,
      })
    }
  }
}

export default connect(props, actions)(Stage)
