import { useCallback, useEffect, useMemo, useRef, useState } from "react"
import { Row, Col, Form, Button } from "antd"
import { useLocation } from 'umi'
import { connect } from "dva"

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'

import s from "./iteration.less"
import { YesIcon, LoaderIcon } from "@/components/common/icons"

const matchKeywords = (dataset, project) => dataset.keywords.some(kw => project.keywords.includes(kw))

const stages = [
  { field: 'candidateTrainSet', option: true, label: 'project.prepare.trainset', tip: 'project.add.trainset.tip', filter: matchKeywords, },
  { field: 'testSet', label: 'project.prepare.validationset', tip: 'project.add.testset.tip', filter: matchKeywords, },
  { field: 'miningSet', label: 'project.prepare.miningset', tip: 'project.add.miningset.tip', },
  { field: 'modelStage', label: 'project.prepare.model', tip: 'tip.task.filter.model', type: 1 },
]

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

const Stage = ({ pid, value, stage, project = {} }) => {
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])
  // const [newProject, updateProject] = useUpdateProject(pid)

  useEffect(() => {
    setValid(value)
  }, [value])

  const renderIcon = () => {
    return valid ? <YesIcon /> : <LoaderIcon />
  }
  const renderState = () => {
    return valid ? t('project.stage.state.done') : t('project.stage.state.waiting')
  }


  const filters = datasets => {
    const fields = stages.filter(({ type, field }) => !type && stage.field !== field)
      .map(({ field }) => field)
    const ids = fields.map(field => project[field]?.id || project[field])
    const notTestingSet = (did) => [...ids, ...(project.testingSets || [])].includes(did) 
    return datasets.filter(dataset => notTestingSet(dataset.id) && (!stage.filter || stage.filter(dataset, project)))
  }

  return <Row wrap={false}>
    <Col flex={'60px'}>
      <div className={s.state}>{renderIcon()}</div>
      <div className={s.state}>{renderState()}</div>
    </Col>
    <Col flex={1}>
      <Form.Item name={stage.field} label={t(stage.label)}
        tooltip={t(stage.tip)} initialValue={value || null}
        rules={[{ required: !stage.option }]}
      >
        <Selection pid={pid} changeByUser filters={filters} allowClear={!!stage.option} />
      </Form.Item>
    </Col>
  </Row>
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  return attr?.id ? attr.id : attr
}

function Prepare({ project = {}, fresh = () => { }, ...func }) {
  const location = useLocation()
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
      updateAndCreateIteration(mergeResult.id)
    }
  }, [mergeResult])

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
      fresh()
      window.location.reload()
    }
  }

  async function updateAndCreateIteration(trainSetVersion) {
    const updateResult = updateProject({ id, trainSetVersion })
    if (updateResult) {
      createIteration()
    }
  }

  function mergeTrainSet() {
    const params = {
      projectId: id,
      dataset: project.trainSetVersion,
      includes: [project.candidateTrainSet]
    }
    merge(params)
  }

  function updatePrepareStatus() {
    const fields = stages.filter(stage => !stage.option).map(stage => stage.field)
    const valid = fields.every(field => project[field]?.id || project[field])
    setValidPrepare(valid)
  }

  function start() {
    if (project.candidateTrainSet) {
      mergeTrainSet()
    } else {
      createIteration()
    }
  }

  return (
    <div className={s.iteration}>
      <Form layout="vertical" onValuesChange={formChange}>
        <Row style={{ justifyContent: 'flex-end' }}>
          {stages.map((stage, index) => (
            <Col key={stage.field} span={6}>
              <Stage stage={stage} value={getAttrFromProject(stage.field, project)} project={project} pid={id} />
            </Col>
          ))}
        </Row>
        <div className={s.createBtn}>
          <Button type='primary' disabled={!validPrepare} onClick={start}>{t('project.prepare.start')}</Button>
        </div>
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
