import { useCallback, useEffect, useState } from "react"
import { Row, Col } from "antd"
import { connect } from "dva"

import { states } from '@/constants/dataset'
import { Stages, StageList } from '@/constants/project'
import Stage from './stage'
import s from "./iteration.less"

function Prepare({ project = {}, fresh = () => { }, ...func }) {
  const [stages, setStages] = useState([])

  useEffect(() => {
    console.log('project init stages:', project)
    project.id && initStages()
  }, [project])

  function initStages() {
    const labels = [
      { value: 'datasets', state: project.miningSet && project.testSet ? states.VALID : -1, url: `/home/project/add/${project.id}?settings=1`, },
      { value: 'model', state: project.model ? states.VALID : -1, url: `/home/project/initmodel/${project.id}`, },
      { value: 'start', state: project.miningSet && project.testSet && project.model ? states.VALID : states.READY, },
    ]
    const ss = labels.map(({ value, state, url, }, index) => {
      const act = `project.iteration.stage.${value}`
      const stage = {
        value: index + 1,
        label: value,
        act,
        // react: `${act}.react`,
        // next: index + 2,
        url,
        state,
        current: index + 1,
        unskippable: true,
        callback: fresh,
      }
      if (index === labels.length - 1) {
        stage.react = ''
        stage.callback = () => createIteration()
        console.log('project:', project, stage)
      }
      return stage
    })
    setStages(ss)
  }

  async function createIteration() {
    const params = {
      iterationRound: 1,
      projectId: project.id,
      prevIteration: 0,
    }
    const result = await func.createIteration(params)
    if (result) {
      fresh()
    }
  }

  return (
    <div className={s.iteration}>
      <Row style={{ justifyContent: 'flex-end' }}>
        {stages.map((stage, index) => (
          <Col key={stage.value} flex={index >= stages.length - 1 ? null : 1}>
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
    createIteration(params) {
      return dispacth({
        type: 'iteration/createIteration',
        payload: params,
      })
    },
    queryTrainDataset(group_id) {
      console.log('group id: ', group_id)
      return dispacth({
        type: 'dataset/queryDatasets',
        payload: { group_id, is_desc: false, limit: 1 }
      })
    }
  }
}

export default connect(props, actions)(Prepare)
