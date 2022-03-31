import { Button, Col, Row, Space } from "antd"
import { useHistory, connect } from "umi"

import t from '@/utils/t'
import { states, statesLabel } from '@/constants/dataset'
import s from './iteration.less'
import { useEffect, useState } from "react"

function Stage({ pid, stage, current = 0, end = false, callback = () => { }, ...func }) {
  // console.log('stage: ', stage, end)
  const history = useHistory()
  const [result, setResult] = useState({})
  const [state, setState] = useState(-1)

  useEffect(() => {
    console.log('stage:', stage)
    setState(stage.state)
  }, [stage])

  useEffect(() => {
    result.state && setState(result.state)
  }, [result])

  useEffect(() => {
    currentStage() && stage.result && fetchStageResult()
  }, [stage.result])

  function skip() {
    callback({
      type: 'skip',
      data: { stage: stage.next },
    })
  }

  function next() {
    if (stage.next) {
      callback({
        type: 'update',
        data: { stage: stage.next },
      })
    } else {
      callback({
        type: 'create',
        data: {
          round: current + 1,
        },
      })
    }
  }

  const currentStage = () => stage.value === stage.current
  const finishStage = () => stage.value < stage.current
  const pendingStage = () => stage.value > stage.current

  const isPending = () => state < 0
  const isReady = () => state === states.READY
  const isValid = () => state === states.VALID
  const isInvalid = () => state === states.INVALID

  function act() {
    stage.url && history.push(stage.url)
  }

  async function fetchStageResult() {
    const resp = await func.getStageResult(stage.result, stage.current)
    console.log('resp:', resp, stage)
    resp && setResult(resp)
  }

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
    const label = isValid() && stage.next ? t('common.step.next') : t(stage.act)
    return <Button disabled={disabled} className={s.act} type='primary' onClick={() => isValid() ? next() : act()}>{label}</Button>
  }

  const renderReactBtn = () => {
    return stage.react && currentStage()
      && (isInvalid() || isValid())
      ? <Button className={s.react} onClick={() => act()}>{t(stage.react)}</Button>
      : null
  }
  const renderState = () => {
    const pending = 'project.stage.state.pending'
    return !finishStage() ? (isPending() ? t(pending) : (result ? result.name : t(statesLabel(state)))) : null
  }

  const renderSkip = () => {
    return !stage.unskippable && !end && currentStage() ? <span className={s.skip} onClick={() => skip()}>{t('common.skip')}</span> : null
  }
  return (
    <div className={stateClass}>
      <Row className={s.row} align='middle' wrap={false}>
        <Col flex={"30px"}><span className={s.num}>{renderCount()}</span></Col>
        <Col>
          <Space>
            {renderMain()}
            {renderReactBtn()}
          </Space>
        </Col>
        {!end ? <Col className={s.lineContainer} hidden={end} flex={1}><span className={s.line}></span></Col> : null}
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
  return {
    userId: state.user.id,
  }
}

const actions = (dispacth) => {
  return {
    getStageResult(id, stage) {
      return dispacth({
        type: 'iteration/getStageResult',
        payload: { id, stage },
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
