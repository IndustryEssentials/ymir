import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { Stages, StageList } from '@/constants/project'
import { templateString } from '@/utils/string'
import Stage from './stage'
import s from "./iteration.less"

function Iteration({ project, fresh = () => { }, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])
  const [prevIteration, setPrevIteration] = useState({})

  useEffect(() => {
    initStages()
  }, [project])

  useEffect(() => {
    if (project.id && project.currentIteration) {
      fetchStagesResult(project.currentIteration)
    }
  }, [project.currentIteration])

  useEffect(() => {
    if (iteration.prevIteration) {
      fetchPrevIteration()
    }
  }, [iteration])

  useEffect(() => {
    iteration.id && rerenderStages()
  }, [iteration, prevIteration])

  const callback = useCallback(iterationHandle, [iteration])

  function initStages() {
    const stageList = StageList()
    const ss = stageList.list.map(({ label, value, url, output, input }) => {
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

    setStages(ss)
  }

  function rerenderStages() {
    const ss = stages.map(stage => {
      const result = iteration[`i${stage.output}`] || iteration[stage.output]
      const urlParams = {
        s0d: project.miningSet.id || 0,
        s0s: project.miningStrategy,
        s0c: project.chunkSize || undefined,
        s1d: iteration.miningSet,
        s1m: prevIteration.model || project.model,
        s2d: iteration.miningResult,
        s3d: prevIteration.trainUpdateSet || project.trainSetVersion,
        s3m: iteration.labelSet,
        s4d: iteration.trainUpdateSet,
        s4t: iteration.testSet,
        id: iteration.id,
        pid: project.id,
        stage: iteration.currentStage,
        output: stage.output,
      }
      const url = templateString(stage.temp || '', urlParams)
      return {
        ...stage,
        iterationId: iteration.id,
        round: iteration.round,
        current: iteration.currentStage,
        url,
        result,
      }
    })
    setStages(ss)
  }

  function iterationHandle({ type = 'update', data = {} }) {
    if (type === 'create') {
      createIteration(data)
    } else if (type === 'skip') {
      skipStage(data)
    } else {
      updateIteration(data)
    }
  }

  async function fetchStagesResult(iteration) {
    const iterationWithResult = await func.getIterationStagesResult(iteration)
    setIteration(iterationWithResult)
  }

  async function fetchPrevIteration() {
    const result = await func.getIteration(project.id, iteration.prevIteration)
    if (result) {
      setPrevIteration(result)
    }
  }

  async function createIteration(data = {}) {
    const params = {
      iterationRound: data.round,
      projectId: project.id,
      prevIteration: iteration.id,
      testSet: project.testSet.id,
    }
    const result = await func.createIteration(params)
    if (result) {
      fresh()
    }
  }
  async function updateIteration(data = {}) {
    const params = {
      id: iteration.id,
      currentStage: data.stage.value,
    }
    const result = await func.updateIteration(params)
    if (result) {
      fetchStagesResult(result)
      // setIteration(result)
    }
  }
  async function skipStage({ stage = {} }) {
    const params = {
      id: iteration.id,
      currentStage: stage.value,
      [stage.input]: 0,
    }
    const result = await func.updateIteration(params)
    if (result) {
      fetchStagesResult(result)
      // setIteration(result)
    }
  }
  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage) => (
          <Col key={stage.value}  flex={stage.next ? 1 : null}>
            <Stage stage={stage} end={!stage.next} callback={callback} />
          </Col>
        ))}
      </Row>
    </div>
  )
}

const props = (state) => {
  return {}
}

const actions = (dispacth) => {
  return {
    getIteration(pid, id) {
      return dispacth({
        type: 'iteration/getIteration',
        payload: { pid, id },
      })
    },
    getIterationStagesResult(iteration) {
      return dispacth({
        type: 'iteration/getIterationStagesResult',
        payload: iteration,
      })
    },
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
    },
    queryFirstTrainDataset(group_id) {
      return dispacth({
        type: 'dataset/queryDatasets',
        payload: { group_id, is_desc: false, limit: 1 }
      })
    }
  }
}

export default connect(props, actions)(Iteration)
