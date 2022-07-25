import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { Row, Col, Form, Button } from "antd"
import { connect } from "dva"

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'

import s from "./iteration.less"
import { YesIcon, LoaderIcon } from "../../../components/common/icons"

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

const Stage = ({ pid, value, stage }) => {
  console.log('stage init value:', value)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])
  // const [newProject, updateProject] = useUpdateProject(pid)

  useEffect(() => {
    setValid(value)
  }, [value])

  const validNext = () => project.miningSet && project.testSet && project.model

  // function initStages() {
  //   const labels = [
  //     { value: 'datasets', state: project.miningSet && project.testSet ? states.VALID : -1, url: `/home/project/${project.id}/iterations/settings`, },
  //     { value: 'model', state: project.model ? states.VALID : -1, url: `/home/project/${project.id}/initmodel`, },
  //     { value: 'start', state: validNext() ? states.VALID : -1, },
  //   ]
  //   const ss = labels.map(({ value, state, url, }, index) => {
  //     const act = `project.iteration.stage.${value}`
  //     const stage = {
  //       value: index,
  //       label: value,
  //       act,
  //       // react: `${act}.react`,
  //       // next: index + 2,
  //       url,
  //       state,
  //       current: index,
  //       unskippable: true,
  //       callback: fresh,
  //     }
  //     if (index === labels.length - 1) {
  //       stage.react = ''
  //       stage.current = validNext() ? index : 0
  //       stage.callback = () => createIteration()
  //     }
  //     return stage
  //   })
  //   setStages(ss)
  // }
  const renderIcon = () => {
    return valid ? <YesIcon /> : <LoaderIcon />
  }
  const renderState = () => {
    return valid ? '已完成' : '待选择'
  }

  return <Row wrap={false}>
    <Col flex={'60px'}>
      <div className={s.state}>{renderIcon()}</div>
      <div className={s.state}>{renderState()}</div>
    </Col>
    <Col flex={1}>
      <Form.Item name={stage.field} label={stage.label}
        tooltip={t(stage.tip)} initialValue={value}
        rules={[{ required: !stage.option }]}
      >
        <Selection pid={pid} changeByUser allowClear={false} />
      </Form.Item>
    </Col>
  </Row>
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  return attr?.id ? attr.id : attr
}

const stages = [
  { field: 'candidateTrainSet', option: true, label: '训练集准备', tip: 'project.add.trainset.tip', },
  { field: 'testSet', label: '测试集准备', tip: 'project.add.testset.tip', },
  { field: 'miningSet', label: '挖掘集准备', tip: 'project.add.miningset.tip', },
  { field: 'modelStage', label: '初始模型准备', tip: 'tip.task.filter.model', type: 1 },
]
function Prepare({ project = {}, fresh = () => { }, ...func }) {
  const prepared = useSelector(({ project }) => project.prepared)
  const [validPrepare, setValidPrepare] = useState(false)
  const [id, setId] = useState(null)
  const [result, updateProject] = useFetch('project/updateProject')
  const [mergeResult, merge] = useFetch('task/merge')

  useEffect(() => {
    project.id && setId(project.id)
    project.id && updatePrepareStatus()
  }, [project])

  useEffect(() => {
    if (result) {
      fresh(result)
    }
  }, [result])

  useEffect(() => {
    if (mergeResult) {
      updateProject({ id, trainSetVersion: mergeResult.id })
    }
  }, [mergeResult])

  useEffect(() => {
    if (prepared) {
      createIteration()
    }
  }, [prepared])

  const formChange = (value, values) => {
    updateProject({ id, ...value })
    updatePrepareStatus(values)
  }

  async function createIteration() {
    const params = {
      iterationRound: 1,
      projectId: project.id,
      prevIteration: 0,
      testSet: project?.testSet?.id,
    }
    const result = await func.createIteration(params)
    if (result) {
      fresh(result)
    }
  }

  function mergeTrainSet() {
    const params = {}
    merge(params)
  }

  function updatePrepareStatus() {
    const fields = stages.filter(stage => !stage.option).map(stage => stage.field)
    const valid = fields.every(field => project[field]?.id || project[field])
    setValidPrepare(valid)
  }

  return (
    <div className={s.iteration}>
      <Form layout="vertical" onValuesChange={formChange}>
        <Row style={{ justifyContent: 'flex-end' }}>
          {stages.map((stage, index) => (
            <Col key={stage.field} span={6}>
              <Stage stage={stage} value={getAttrFromProject(stage.field, project)} pid={id} />
            </Col>
          ))}
        </Row>
        <div className={s.createBtn}><Button type='primary' disabled={!validPrepare} onClick={createIteration}>使用迭代功能提升模型效果</Button></div>
      </Form>
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
