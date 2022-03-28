import { useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { states } from '@/constants/dataset'
import { Stages, StageList } from '@/constants/project'
import Stage from './stage'
import s from "./iteration.less"

function Prepare({ project = {}, fresh = () => {}, ...func }) {
  const [stages, setStages] = useState([])

  useEffect(() => {
    project.id && initStages()
  }, [project])

  function initStages() {
    const labels = [
      { value: 'datasets', url: `/home/project/add/${project.id}?settings=1`, },
      { value: 'model', url: `/home/project/initmodel/${project.id}`, },
      { value: 'start', callback: () => fresh() },
    ]
    const ss = labels.map(({ value, url, callback }, index) => {
      const act = `project.iteration.stage.${value}`
      const stage = {
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
      if (index === labels.length - 1) {
        const prepared = project.miningSet && project.testSet && project.trainSet
        stage.state = prepared ?  -1 : states.READY
        stage.react = ''
        console.log('project:', project, prepared, stage)
      }
      return stage
    })
    setStages(ss)
  }

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage, index) => (
          <Col key={stage.value} flex={index >= stages.length - 1? null : 1}>
            <Stage pid={project.id} stage={stage} end={index >= stages.length - 1} callback={stage.callback} />
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
