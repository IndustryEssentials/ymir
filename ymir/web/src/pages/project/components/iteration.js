import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { Stages, StageList } from '@/constants/project'
import { templateString } from '@/utils/string'
import Stage from './stage'
import s from "./iteration.less"

function Iteration({ project, fresh = () => {}, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])

  useEffect(() => {
    initStages()
  }, [])
  useEffect(() => {
    project.id && fetchIteration()
  }, [project])

  useEffect(() => {
    iteration.id && rerenderStages(iteration)
  }, [iteration])

  const callback = useCallback(iterationHandle, [iteration])

  function initStages() {
    const labels = ['ready', 'mining', 'label', 'merge', 'training', 'next']
    const stageList = StageList()
    const ss = stageList.list.map(({ value, url, prepare, resultKey }) => {
      const label = `project.iteration.stage.${labels[value]}`
      return {
        value: value,
        label,
        act: label,
        react: `${label}.react`,
        state: -1,
        next: stageList[value].next,
        url,
        prepare,
        resultKey,
        project,
        unskippable: [Stages.merging, Stages.training].includes(value),
        callback,
      }
    })

    setStages(ss)
  }

  function rerenderStages(iteration) {
    const ss = stages.map(stage => {
      const result = iteration[stage.resultKey] || {}
      const url = templateString(stage.url || '', { ...project, ...iteration,})
      console.log('url:', url, { ...project, ...iteration })
      return {
        ...stage,
        iterationId: iteration.id,
        round: iteration.round,
        current: iteration.currentStage,
        url,
        state: result.state || -1,
        result,
      }
    })
    setStages(ss)
  }

  function iterationHandle({ type = 'update', data = {}}) {
    if (type === 'create') {
      createIteration(data)
    } else {
      updateIteration(data)
    }
  }

  function fetchIteration() {
    // const result = await func.getIteration(project.id, project?.currentIteration?.id)
    // if (result) {
      setIteration(project?.currentIteration)
    // }
  }
  async function createIteration(data = {}) {
    const params = {
      // currentStage: 0
      iterationRound: data.round,
      miningDataset: iteration.miningSet,
      trainingModel: iteration.model,
      prevTrainingDataset: iteration.trainUpdateSet,
      projectId: project.id,
    }
    const result = await func.createIteration(params)
    if (result) {
      fresh()
    }
  }
  async function updateIteration(data = {}) {
    const params = {
      id: iteration.id,
      currentStage: data.stage,
      miningDataset: iteration.miningSet,
      trainingModel: iteration.model,
      prevTrainingDataset: iteration.trainSet,
      miningResult: iteration.miningResult,
      labelResult: iteration.labelSet,
      traningDataset: iteration.trainUpdateSet,
    }
    const result = await func.updateIteration(params)
    if (result) {
      setIteration(result)
    }
  }
  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage) => (
          <Col key={stage.value} flex={1}>
            <Stage stage={stage} end={!stage.next} />
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

export default connect(props, actions)(Iteration)
