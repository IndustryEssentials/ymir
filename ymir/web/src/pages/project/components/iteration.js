import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { Stages, StageList } from '@/constants/project'
import Stage from './stage'
import s from "./iteration.less"

function Iteration({ project, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])

  useEffect(() => {
    initStages()
  }, [])
  useEffect(() => {
    project.id && fetchIteration()
  }, [project])

  useEffect(() => {
    rerenderStages(iteration)
  }, [iteration])

  function initStages() {
    const labels = ['ready', 'mining', 'label', 'merge', 'training', 'next']
    const stageList = StageList()
    const ss = stageList.list.map(stage => {
      const label = `project.iteration.stage.${labels[stage]}`
      return {
        value: stage,
        label,
        act: label,
        react: `${label}.react`,
        state: -1,
        next: stageList[stage].next,
        unskippable: [Stages.merging, Stages.training].includes(stage),
      }
    })

    setStages(ss)
  }

  function rerenderStages() {

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
            <Stage stage={stage} current={2} end={!stage.next} />
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
