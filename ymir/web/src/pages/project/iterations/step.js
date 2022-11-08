import { Col, Popover, Row } from "antd"
import { useSelector } from "umi"

import t from "@/utils/t"
import { states, statesLabel } from "@/constants/dataset"
import s from "./iteration.less"
import { STEP } from "@/constants/iteration"
import { useEffect, useState } from "react"
import RenderProgress from "../../../components/common/Progress"
import { YesIcon } from "@/components/common/Icons"
import VersionName from "@/components/result/VersionName"

function Step({ step }) {
  const result = useSelector((state) => {
    const res = step.resultType ? state[step.resultType][step.resultType] : {}
    return res[step.resultId] || {}
  })
  const [state, setState] = useState(-1)

  useEffect(() => {
    const st = typeof result?.state !== "undefined" ? result.state : step.state
    setState(st)
  }, [result?.state, step])

  const currentStep = () => step.value === step.current
  const finishStep = () => step.finished
  const pendingStep = () => !step.finished && !currentStep()

  const isPending = () => state < 0
  const isReady = () => state === states.READY
  const isValid = () => state === states.VALID
  const isInvalid = () => state === states.INVALID

  const stateClass = `${s.step} ${
    currentStep() ? s.current : finishStep() ? s.finish : s.pending
  }`

  const renderCount = () => {
    const content =
      finishStep() || (currentStep() && isValid()) ? (
        <YesIcon />
      ) : (
        step.index + 1
      )
    const cls = pendingStep() ? s.pending : currentStep() ? s.current : s.finish
    return <span className={`${s.num} ${cls}`}>{content}</span>
  }

  const renderState = () => {
    const pendingLabel = "project.stage.state.pending"
    const valid = result.name ? (
      <VersionName result={result} />
    ) : step.end ? null : (
      t("common.done")
    )
    const currentPending = t("project.stage.state.pending.current")
    const currentState = isReady()
      ? RenderProgress(state, result, true)
      : t(statesLabel(state))
    const notValid = (
      <span className={s.current}>
        {isPending() && currentStep() ? currentPending : currentState}
      </span>
    )
    const pending = <span className={s.pending}>{t(pendingLabel)}</span>
    return !pendingStep() ? (isValid() ? valid : notValid) : pending
  }

  return (
    <div className={stateClass}>
      <Row className={s.row} align="middle" wrap={false}>
        <Col flex={"30px"}>{renderCount()}</Col>
        <Col>{t(step.act)}</Col>
        {!step.end ? (
          <Col className={s.lineContainer} flex={1}>
            <span className={s.line}></span>
          </Col>
        ) : null}
      </Row>
      <Row className={s.row}>
        <Col flex={"30px"}>&nbsp;</Col>
        <Col className={s.state} flex={1}>
          {renderState()}
        </Col>
      </Row>
    </div>
  )
}

export default Step
