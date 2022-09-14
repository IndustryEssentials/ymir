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

const matchKeywords = (dataset, project) => dataset.keywords.some(kw => project.keywords?.includes(kw))

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

export default function Stage ({ pid, stage, project = {} }) {
  const [value, setValue] = useState(null)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])

  useEffect(() => {
    setValid(value)
  }, [value])

  useEffect(() => {
    const value = getAttrFromProject(stage.field, project)
    console.log('test value:', value, stage.field, project)
    setValue(value)
  }, [stage, project])

  const renderIcon = () => {
    return valid ? <YesIcon /> : <LoaderIcon />
  }
  const renderState = () => {
    return valid ? t('project.stage.state.done') : t('project.stage.state.waiting')
  }

  const filters = datasets => {
    return datasets
    // const fields = stages.filter(({ type, field }) => !type && stage.field !== field).map(({ field }) => field)
    // const ids = fields.map(field => project[field]?.id || project[field])
    // const notTestingSet = (did) => ![...ids, ...(project.testingSets || [])].includes(did)
    // return datasets.filter(dataset => notTestingSet(dataset.id) && (!stage.filter || stage.filter(dataset, project)))
  }

  return <Row wrap={false}>
    <Col flex={'60px'}>
      <div className={s.state}>{renderIcon()}</div>
      <div className={s.state}>{renderState()}</div>
    </Col>
    <Col flex={1}>
      {/* <Form.Item name={stage.field} label={t(stage.label)}
        tooltip={t(stage.tip)}
        rules={[{ required: !stage.option }]}
      > */}
        <Selection value={value} pid={pid} changeByUser filters={filters} allowClear={!!stage.option} />
      {/* </Form.Item> */}
    </Col>
  </Row>
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  console.log('field, project:', field, project, attr)
  return attr?.id ? attr.id : attr
}
