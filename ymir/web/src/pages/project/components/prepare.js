import { useCallback, useEffect, useState } from "react"
import { Row, Col, Form, Button } from "antd"
import { connect } from "dva"

import { states } from '@/constants/dataset'
import useUpdateProject from '@/hooks/useUpdateProject'
import DatasetSelect from '@/components/form/DatasetSelect'
import ModelSelect from '@/components/form/ModelSelect'

import s from "./iteration.less"

const SettingsSelection = (Select) => {
  const Selection = ({ field, callback = () => { }, ...props }) => {
    const [newProject, updateProject] = useUpdateProject()
    const onChange = async (value) => {
      await updateProject({ [field]: value })
      callback(newProject)
    }

    return <Select {...props} onChange={onChange} />
  }
  return Selection
}

const Stage = ({ project, stage }) => {
  const [valid, setValid] = useState(false)
  const Selection = SettingsSelection(stage.type ? ModelSelect : DatasetSelect)

  useEffect(() => {
    project && setValid(project[stage.field])
  }, [project])

  const validNext = () => project.miningSet && project.testSet && project.model

  function initStages() {
    const labels = [
      { value: 'datasets', state: project.miningSet && project.testSet ? states.VALID : -1, url: `/home/project/${project.id}/iterations/settings`, },
      { value: 'model', state: project.model ? states.VALID : -1, url: `/home/project/${project.id}/initmodel`, },
      { value: 'start', state: validNext() ? states.VALID : -1, },
    ]
    const ss = labels.map(({ value, state, url, }, index) => {
      const act = `project.iteration.stage.${value}`
      const stage = {
        value: index,
        label: value,
        act,
        // react: `${act}.react`,
        // next: index + 2,
        url,
        state,
        current: index,
        unskippable: true,
        callback: fresh,
      }
      if (index === labels.length - 1) {
        stage.react = ''
        stage.current = validNext() ? index : 0
        stage.callback = () => createIteration()
      }
      return stage
    })
    setStages(ss)
  }
  const renderIcon = () => {
    return valid ? <YesIcon /> : 'wait'
  }
  const renderState = () => {
    return valid ? '已完成' : '待选择'
  }
  return <Col flex={1}>
    <Row>
      <Col flex={'60px'}>
        <div className={s.state}>{renderIcon()}</div>
        <div className={s.state}>{renderState()}</div>
      </Col>
      <Col flex={1}>
        <Form.Item label={stage.label}></Form.Item>
        <Selection field={stage.field} callback={stage.callback} />
      </Col>
    </Row>
  </Col>
}

function Prepare({ project = {}, fresh = () => { }, ...func }) {
  const [validPrepare, setValidPrepare] = useState(false)

  const stages = [
    { field: 'trainSet', },
    { field: 'testSet', },
    { field: 'miningSet', },
    { field: 'model', type: 1 },
  ]

  useEffect(() => {
    const valid = stages.reduce((prev, curr) => prev && project[curr[field]], false)
    setValidPrepare(valid)
  }, [project])

  async function createIteration() {
    const params = {
      iterationRound: 1,
      projectId: project.id,
      prevIteration: 0,
      testSet: project?.testSet?.id,
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
          <Col key={stage.field} flex={1}>
            <Stage stage={{ ...stage, callback: fresh }} project={project} />
          </Col>
        ))}
      </Row>
      <div className={s.createBtn}><Button type='primary' disabled={validPrepare} onClick={createIteration}>使用迭代功能提升模型效果</Button></div>
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
      return dispacth({
        type: 'dataset/queryDatasets',
        payload: { group_id, is_desc: false, limit: 1 }
      })
    }
  }
}

export default connect(props, actions)(Prepare)
