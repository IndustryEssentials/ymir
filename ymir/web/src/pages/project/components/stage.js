import { Button, Col, Row, Space } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import { states } from '@/constants/dataset'
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

  const currentStage = () => current === stage.id
  const finishStage = () => stage.id < current
  const pendingStage = () => stage.id > current

  const isReady = () => [TASKSTATES.READY].includes(stage.taskState)

  const stateClass = `${s.stage} ${currentStage() ? s.current : (finishStage() ? s.finish : s.pending)}`

  const renderCount = () => {
    if (finishStage() || (currentStage() && stage.taskState === TASKSTATES.FINISH)) {
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
    const disabled = !([TASKSTATES.PENDING, TASKSTATES.FINISH].includes(stage.taskState) || false)
    const label = [TASKSTATES.PENDING, TASKSTATES.DOING].includes(stage.taskState) ? t(stage.act) : '下一步'
    return <Button disabled={disabled} className={s.act} type='primary' onClick={() => next()}>{label}</Button>
  }

  const renderReactBtn = () => {
    return stage.react && currentStage()
      && [TASKSTATES.FINISH, TASKSTATES.ERROR, TASKSTATES.TERMINATED].includes(stage.taskState)
      ? <Button className={s.react}>{t(stage.react)}</Button>
      : null
  }
  const renderState = (state) => {
    const pending = 'project.stage.state.pending'
    const result = stage.result
    return result ? result : t(currentStage() ? getTaskStateLabel(stage.taskState) : pending)
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
