import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { Stages, StageList } from '@/constants/project'
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

  function initStages() {
    const labels = ['ready', 'mining', 'label', 'merge', 'training', 'next']
    const stageList = StageList()
    const ss = stageList.list.map(({ value, url, prev, resultKey }) => {
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
        unskippable: [Stages.merging, Stages.training].includes(value),
        callback: stageList[value].next ? fetchIteration : fresh(),
      }
    })

    setStages(ss)
  }

  function rerenderStages(iteration) {
    const ss = stages.map(stage => {
      const prepareId = iteration[stage.prepare]
      const result = iteration[stage.resultKey]
      return {
        ...stage,
        iterationId: iteration.id,
        round: iteration.round,
        current: iteration.current,
        url: `${stage.url}${prepareId}?iterationId=${iteration.id}&stage=${stage.value}`,
        state: result.state,
        result,
      }
    })
    setStages(ss)
  }

  async function fetchIteration() {
    const result = await func.getIteration(project.id, project.currentIteration)
    if (result) {
      setIteration(result)
    }
  }
  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage) => (
          <Col key={stage.id} flex={1}>
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
  }
}

export default connect(props, actions)(Iteration)
