import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"

import { getSteps, STEP } from "@/constants/iteration"
import useFetch from "@/hooks/useFetch"

import Step from "./step"
import StepAction from "./stepAction"
import s from "./iteration.less"

function Iteration({ project, fresh = () => {} }) {
  const [iteration, setIteration] = useState({})
  const [_, getIteration] = useFetch("iteration/getIteration", {})
  const [steps, setSteps] = useState([])
  const [selectedStep, setSelectedStep] = useState(null)
  const [createResult, create] = useFetch("iteration/createIteration")
  const [_b, bind] = useFetch("iteration/bindStep")
  const [_n, next] = useFetch("iteration/nextStep")
  const [_k, skip] = useFetch("iteration/skipStep")

  useEffect(() => {
    if (project.id && project.currentIteration) {
      setIteration(project.currentIteration)
    }
  }, [
    project?.currentIteration,
    iteration?.needReload,
    project?.currentIteration?.currentStep,
  ])

  useEffect(() => {
    iteration.id && generateSteps()
  }, [iteration])

  useEffect(() => {
    ;(createResult || _b || _n || _k) && fresh()
  }, [createResult, _b, _n, _k])

  const callback = useCallback(iterationHandle, [iteration])

  function generateSteps() {
    const list = getSteps()
    const steps = list.map((step, index) => {
      const remoteStep = iteration.steps[index] || {}
      const current = iteration?.currentStep?.name || STEP.next
      return {
        ...step,
        ...remoteStep,
        index,
        current,
        selected: selectedStep,
      }
    })
    setSteps(steps)
  }

  const getParams = (data = {}) => ({
    id: iteration.id,
    sid: iteration?.currentStep?.id,
    ...data,
  })

  function iterationHandle({ type = "bind", data = {} }) {
    switch (type) {
      case "bind":
        bind(
          getParams({
            tid: data.taskId,
          })
        )
        break
      case "create":
        createIteration(data)
        break
      case "skip":
        skip(getParams())
        break
      case "next":
        next(getParams())
    }
  }

  function createIteration() {
    const params = {
      iterationRound: project.round + 1,
      projectId: project.id,
      prevIteration: iteration.id,
      testSet: project.testSet.id,
      miningSet: project.miningSet.id,
    }
    create(params)
  }

  function goStep(step) {
    console.log("step:", step)
    setSelectedStep(step.value)
  }

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: "flex-end" }}>
        {steps.map((step) => (
          <Col key={step.value} flex={!step.end ? 1 : null}>
            <Step step={step} goStep={goStep} />
          </Col>
        ))}
      </Row>
      <div className={s.stepContent}>
        <StepAction
          steps={steps}
          iteration={iteration}
          project={project}
          callback={callback}
        />
      </div>
    </div>
  )
}

export default Iteration
