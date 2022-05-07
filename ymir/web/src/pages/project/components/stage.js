import { Button, Col, Popover, Row, Space } from "antd"
import { useHistory, connect } from "umi"

import t from '@/utils/t'
import { states, statesLabel } from '@/constants/dataset'
import s from './iteration.less'
import { useEffect, useState } from "react"
import RenderProgress from "../../../components/common/progress"
import { YesIcon } from '@/components/common/icons'    

function Stage({ pid, stage, stageResult, current = 0, end = false, callback = () => { }, ...func }) {
  const history = useHistory()
  const [result, setResult] = useState({})
  const [state, setState] = useState(-1)

  useEffect(() => {
    const st = typeof result.state !== 'undefined' ? result.state : stage.state
    setState(st)
  }, [result, stage])

  useEffect(() => {
    currentStage() && func.setCurrentStageResult(stage.result)
  }, [stage.result])

  useEffect(() => {
    const res = currentStage() && stageResult?.id === stage?.result?.id ? stageResult : stage.result
    setResult(res || {})
  }, [stage.result, stageResult])

  useEffect(() => {
    if (stageResult?.id !== stage.result?.id) {
      return
    }
    if (stageResult.needReload) {
      fetchStageResult(true)
    }
  }, [stageResult])

  function skip() {
    callback({
      type: 'skip',
      data: { stage: stage.next },
    })
  }

  function next() {
    if (isValid()) {
      callback({
        type: 'update',
        data: { stage: stage.next },
      })
    } else {
      act()
    }
  }

  function ending() {
    if (end) {
      callback({
        type: 'create',
        data: {
          round: stage.round + 1,
        },
      })
    } else {
      act()
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

  async function fetchStageResult(force) {
    await func.getStageResult(stage.result?.id, stage.current, force)
  }

  const stateClass = `${s.stage} ${currentStage() ? s.current : (finishStage() ? s.finish : s.pending)}`

  const renderCount = () => {
    const content = finishStage() || (currentStage() && isValid()) ? <YesIcon /> : stage.value + 1
    const cls = pendingStage() ? s.pending : (currentStage() ? s.current : s.finish)
    return <span className={`${s.num} ${cls}`}>{content}</span>
  }
  const renderMain = () => {
    return currentStage() ? renderMainBtn() : <span className={s.act}>{t(stage.act)}</span>
  }

  const renderMainBtn = () => {
    // show by task state and result
    const content = RenderProgress(result.state, result, true)
    const disabled = isReady() || isInvalid()
    const label = isValid() && stage.next ? t('common.step.next') : t(stage.act)
    const btn = <Button disabled={disabled} type='primary' onClick={() => stage.next ? next() : ending()}>{label}</Button>
    const pop = <Popover content={content}>{btn}</Popover>
    return result.id ? pop : btn
  }

  const renderReactBtn = () => {
    return stage.react && currentStage()
      && (isInvalid() || isValid())
      ? <Button className={s.react} onClick={() => act()}>{t(stage.react)}</Button>
      : null
  }
  const renderState = () => {
    const pending = 'project.stage.state.pending'
    return !pendingStage() ? 
      (isValid() ?  
        (result.name ?`${result.name} ${result.versionName}` : 
          (end ? null : t('common.done'))) : 
        <span className={s.current}>{isPending() && currentStage() ? t('project.stage.state.pending.current') : t(statesLabel(state))}</span>) : 
      <span className={s.pending}>{t(pending)}</span>
  }

  const renderSkip = () => {
    return !stage.unskippable && !end && currentStage() ? <span className={s.skip} onClick={() => skip()}>{t('common.skip')}</span> : null
  }
  return (
    <div className={stateClass}>
      <Row className={s.row} align='middle' wrap={false}>
        <Col flex={"30px"}>{renderCount()}</Col>
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
          {renderState()}
        </Col>
        <Col>{renderSkip()}</Col>
      </Row>
    </div>
  )
}

const props = (state) => {
  return {
    userId: state.user.id,
    stageResult: state.iteration.currentStageResult,
  }
}

const actions = (dispacth) => {
  return {
    getStageResult(id, stage, force) {
      return dispacth({
        type: 'iteration/getStageResult',
        payload: { id, stage, force },
      })
    },
    setCurrentStageResult(result) {
      return dispacth({
        type: 'iteration/setCurrentStageResult',
        payload: result,
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
