import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { states } from '@/constants/dataset'
import { Stages, StageList } from '@/constants/project'
import Stage from './stage'
import s from "./iteration.less"

function Prepare({ project = {}, fresh = () => {}, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])

  useEffect(() => {
    initStages()
  }, [])
  useEffect(() => {
    project.id && rerenderStages(project)
  }, [project])

  function initStages() {
    const labels = [
      { value: 'datasets', url: '/home/project/add?settings=1', state: states.READY, },
      { value: 'model', url: '/home/project/modelSettings', state: states.READY, },
      { value: 'start', state: states.INVALID, callback: () => fresh() },
    ]
    const ss = labels.map(({ value, url, state, callback }, index) => {
      const act = `project.iteration.stage.${value}`
      return {
        value: index + 1,
        label: value,
        act,
        react: `${act}.react`,
        next: index + 2,
        url,
        state: -1,
        current: index + 1,
        unskippable: true,
        callback,
      }
    })

    setStages(ss)
  }

  function rerenderStages(project) {
    const ss = stages.map((stage, index) => {
      if (index === stages.length - 1) {
        stage.state = project.currentIteration > 0 ? states.READY : states.INVALID
        stage.react = ''
      }
      return { ...stage }
    })
    setStages(ss)
  }

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage, index) => (
          <Col key={stage.value} flex={index >= stages.length - 1? null : 1}>
            <Stage stage={stage} end={index >= stages.length - 1} callback={stage.callback} />
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
