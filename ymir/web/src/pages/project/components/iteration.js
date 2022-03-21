import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import Stage from './stage'
import s from "./iteration.less"

function Iteration({ id, ...func }) {
  const [iteration, setIteration] = useState({})
  const [stages, setStages] = useState([])

  useEffect(() => {
    id && fetchIteration()
  }, [id])

  const iterationStages = [
    { id: 1, value: 1, act: 'project.iteration.stage.ready', react: 'project.iteration.stage.ready.react', state: 1 },
    { id: 2, value: 2, act: 'project.iteration.stage.mining', react: 'project.iteration.stage.mining.react', state: 2 },
    { id: 3, value: 3, act: 'project.iteration.stage.label', react: 'project.iteration.stage.label.react', state: 3 },
    { id: 4, value: 4, act: 'project.iteration.stage.merge', react: 'project.iteration.stage.merge.react', state: 4 },
    { id: 5, value: 5, act: 'project.iteration.stage.training', react: 'project.iteration.stage.training.react', state: 5, unskippable: true, },
    { id: 6, value: 6, act: 'project.iteration.stage.next', state: 6 },
  ]

  async function fetchIteration() {
    const result = await func.getIteration(id)
    if (result) {
      setIteration(result)
    }
  }
  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {iterationStages.map((stage) => (
          <Col key={stage.id} flex={1}>
            <Stage stage={stage} current={3} end={stage.id === iterationStages.length} />
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
    getIteration(id) {
      return dispacth({
        type: 'iteration/getIteration',
        payload: id,
      })
    }
  }
}

export default connect(props, actions)(Iteration)
