import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"
import { useSelector } from "umi"

import { getSteps } from "@/constants/iteration"
import { templateString } from "@/utils/string"
import useFetch from "@/hooks/useFetch"

import Step from "./step"
import StepAction from "./stepAction"
import s from "./iteration.less"

function Iteration({ project, fresh = () => {} }) {
  const iteration = useSelector(
    ({ iteration }) => iteration.iteration[project.currentIteration?.id] || {}
  )
  const [_, getIteration] = useFetch("iteration/getIteration", {})
  const [steps, setSteps] = useState([])
  const [prevIteration, getPrevIteration] = useFetch(
    "iteration/getIteration",
    {}
  )
  const [createResult, create] = useFetch("iteration/createIteration")
  const [_b, bind] = useFetch("iteration/bindStep")
  const [_n, next] = useFetch("iteration/nextStep")
  const [_k, skip] = useFetch("iteration/skipStep")

  useEffect(() => {
    if ((project.id && project.currentIteration) || iteration?.needReload) {
      getIteration({
        pid: project.id,
        id: project.currentIteration?.id,
        more: true,
      })
    }
  }, [project.currentIteration, iteration?.needReload])

  useEffect(
    () =>
      iteration.prevIteration &&
      getPrevIteration({
        pid: project.id,
        id: iteration.prevIteration,
      }),
    [iteration]
  )

  useEffect(() => {
    iteration.id && generateSteps()
  }, [iteration, prevIteration])

  useEffect(() => createResult && fresh(), [createResult])

  const callback = useCallback(iterationHandle, [iteration])

  function generateSteps() {
    const list = getSteps()
    const steps = list.map((step, index) => {
      const remoteStep = iteration.steps[index] || {}
      const current = iteration.currentStep.name
      return {
        ...step,
        ...remoteStep,
        index: index + 1,
        current,
      }
    })
    setSteps(steps)
  }

  const getParams = (data = {}) => ({
    id: iteration.id,
    sid: iteration.currentStep.id,
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

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: "flex-end" }}>
        {steps.map((step) => (
          <Col key={step.value} flex={step.next ? 1 : null}>
            {console.log("steps:", steps)}
            <Step step={step} end={!step.next} />
          </Col>
        ))}
      </Row>
      <div className={s.stepContent}>
        <StepAction
          steps={steps}
          iteration={iteration}
          project={project}
          prevIteration={prevIteration}
          callback={callback}
        />
      </div>
    </div>
  )
}

export default Iteration
