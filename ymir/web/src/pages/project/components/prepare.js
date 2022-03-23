import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { states } from '@/constants/dataset'
import { Stages, StageList } from '@/constants/project'
import Stage from './stage'
import s from "./iteration.less"

function Prepare({ project, fresh = () => {}, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])

  useEffect(() => {
    initStages()
  }, [])
  useEffect(() => {
    project.id && rerenderStages(project)
  }, [project])

  useEffect(() => {
    iteration?.id && rerenderStages(iteration)
  }, [iteration])

  function initStages() {
    const labels = [
      { value: 'datasets', url: '/home/project/add?settings=1', state: states.READY, },
      { value: 'model', url: '/home/project/modelSettings', state: states.READY, },
      { value: 'start', state: states.INVALID, callback: () => fresh() },
    ]
    const ss = labels.map(({ value, url, state, callback }, index) => {
      const act = `project.iteration.stage.${value}`
      return {
        value: index,
        label,
        act,
        react: `${act}.react`,
        next: index + 1,
        url,
        state,
        unskippable: true,
        callback,
      }
    })

    setStages(ss)
  }

  function rerenderStages(project) {
    const ss = stages.map((stage, index) => {
      if (index === stages.length - 1) {
        stage.state = project.round > 0 ? states.READY : states.INVALID
      }
      return stage
    })
    setStages(ss)
  }

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage) => (
          <Col key={stage.id} flex={1}>
            <Stage stage={stage} current={iteration.current} end={!stage.next} callback={stage.callback} />
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

export default connect(props, actions)(Prepare)
