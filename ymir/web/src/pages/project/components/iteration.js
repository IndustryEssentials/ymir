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
  const [prevIteration, setPrevIteration] = useState({})
  const [firstTrainSet, setFirstTrainSet] = useState({})

  useEffect(() => {
    initStages()
  }, [])
  useEffect(() => {
    if (project.id && project.currentIteration) {
      setIteration(project.currentIteration)
    }
  }, [project])

  useEffect(() => {
    if (iteration.prevIteration) {
      fetchPrevIteration()
    } else {
      fetchFirstTrainSet()
    }
    
  }, [iteration])

  useEffect(() => {
    console.log('rerender iteration: ', iteration, firstTrainSet)
    iteration.id && rerenderStages()
  }, [iteration, firstTrainSet])

  const callback = useCallback(iterationHandle, [iteration])

  function initStages() {
    const labels = ['ready', 'mining', 'label', 'merge', 'training', 'next']
    const stageList = StageList()
    const ss = stageList.list.map(({ value, url, output, input }) => {
      const label = `project.iteration.stage.${labels[value]}`
      return {
        value: value,
        label,
        act: label,
        react: `${label}.react`,
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
      const result = iteration[stage.output]
      const url = templateString(stage.temp || '', {
        s0d: project.miningSet.id || 0,
        s0s: project.miningStrategy,
        s0c: project.chunkSize || undefined,
        s1d: iteration.miningSet,
        s1m: prevIteration.model || project.model,
        s2d: iteration.miningResult,
        s3d: prevIteration.trainUpdateSet || firstTrainSet.id,
        s3m: iteration.labelSet,
        s4d: iteration.trainUpdateSet,
        s4t: project?.testSet?.id,
        id: iteration.id,
        pid: project.id,
        stage: iteration.currentStage,
        output: stage.output,
      })
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

  function iterationHandle({ type = 'update', data = {}}) {
    if (type === 'create') {
      createIteration(data)
    } else if (type === 'skip') {
      skipStage(data)
    } else {
      updateIteration(data)
    }
  }

  async function fetchPrevIteration() {
    const result = await func.getIteration(project.id, iteration.prevIteration)
    if (result) {
      setPrevIteration(result)
    }
  }

  async function fetchFirstTrainSet() {
    const result = await func.queryFirstTrainDataset(project.trainSet.id)
    if (result) {
      const { items: [ds]} = result
      ds && setFirstTrainSet(ds)
    }
  }

  async function createIteration(data = {}) {
    const params = {
      iterationRound: data.round,
      projectId: project.id,
      prevIteration: iteration.id,
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
      setIteration(result)
    }
  }
  async function skipStage({ stage = {}}) {
    const params = {
      id: iteration.id,
      currentStage: stage.value,
      [stage.output]: 0,
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
      console.log('group id: ', group_id)
      return dispacth({
        type: 'dataset/queryDatasets',
        payload: { group_id, is_desc: false, limit: 1 }
      })
    }
  }
}

export default connect(props, actions)(Iteration)
