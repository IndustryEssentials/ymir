import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"
import { useSelector } from "umi"

import { Stages, StageList } from "@/constants/iteration"
import { templateString } from "@/utils/string"
import useFetch from "@/hooks/useFetch"

import Stage from "./stage"
import StepAction from "./stepAction"
import s from "./iteration.less"

function Iteration({ project, fresh = () => {} }) {
  const iteration = useSelector(
    ({ iteration }) => iteration.iteration[project.currentIteration?.id] || {}
  )
  const [_, getIteration] = useFetch("iteration/getIteration", {})
  const [stages, setStages] = useState([])
  const [prevIteration, getPrevIteration] = useFetch(
    "iteration/getIteration",
    {}
  )
  const [createResult, create] = useFetch("iteration/createIteration")
  const [_b, bind] = useFetch("iteration/bindStep")
  const [_n, next] = useFetch("iteration/nextStep")
  const [_k, skip] = useFetch("iteration/skipStep")
  const [_u, update] = useFetch("iteration/updateIteration")

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
    iteration.id && rerenderStages()
  }, [iteration, prevIteration])

  useEffect(() => createResult && fresh(), [createResult])

  const callback = useCallback(iterationHandle, [iteration])

  function getInitStages() {
    const stageList = StageList()
    return stageList.list.map(({ label, value, url, output, input }) => {
      const slabel = `project.iteration.stage.${label}`
      return {
        value: value,
        label,
        act: slabel,
        react: `${slabel}.react`,
        state: -1,
        next: stageList[value].next,
        temp: url,
        output,
        input,
        project,
        unskippable: [Stages.merging, Stages.training].includes(value),
        callback,
      }
    })
  }

  function rerenderStages() {
    const initStages = getInitStages()
    const ss = initStages.map((stage) => {
      const result = iteration[stage.output]
      return {
        ...stage,
        iterationId: iteration.id,
        round: iteration.round,
        current: iteration.currentStage,
        result,
      }
    })
    setStages(ss)
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
        {stages.map((stage) => (
          <Col key={stage.value} flex={stage.next ? 1 : null}>
            <Stage stage={stage} end={!stage.next} callback={callback} />
          </Col>
        ))}
      </Row>
      <div className={s.stepContent}>
        <StepAction
          stages={stages}
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
