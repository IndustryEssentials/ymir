import { useCallback, useEffect, useMemo, useState } from "react"
import { Row, Col, Form, Button, Space } from "antd"
import { useHistory } from "umi"

import { runningDataset } from '@/constants/dataset'
import t from '@/utils/t'
import { generateName } from '@/utils/string'
import useFetch from '@/hooks/useFetch'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'
import Uploader from '@/components/form/uploader'

import s from "./iteration.less"
import { YesIcon, LoaderIcon, AddIcon, TrainIcon, ImportIcon } from "@/components/common/icons"
import RenderProgress from "@/components/common/progress"

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

export default function Stage({ pid, stage, form, project = {}, result, update }) {
  const history = useHistory()
  const [value, setValue] = useState(null)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])
  const [candidateList, setCandidateList] = useState(true)
  const [file, setFile] = useState({ name: '', url: '' })
  const [addResult, addDataset] = useFetch('dataset/createDataset')

  useEffect(() => {
    setValid(value)
  }, [value])

  useEffect(() => {
    const value = getAttrFromProject(stage.field, project)
    setValue(value)
    setFieldValue(value)
  }, [stage, project])

  useEffect(() => {
    file.url && addDataset({
      ...file,
      projectId: pid,
    })
  }, [file])

  useEffect(() => {
    if (addResult?.id) {
      update({ [stage.field]: addResult.id })
    }
  }, [addResult])

  const setFieldValue = value => form.setFieldsValue({
    [stage.field]: value || null,
  })

  const goTraining = () => {
    const iparams = `from=iteration`
    history.push(`/home/project/${pid}/train?did=${project.candidateTrainSet}&test=${project.testSet.id}&${iparams}`)
  }

  const filters = stage.filter ? useCallback(datasets => {
    const result = stage.filter(datasets, project)
    setCandidateList(!stage.type ? !!result.filter(item => item.assetCount).length : !!result.length)
    return result
  }, [stage.field, project]) : null

  const renderEmptyState = (type) => !type ?
    <Button 
    type="primary" 
    block 
    icon={<AddIcon />} 
    onClick={() => history.push(`/home/project/${pid}/dataset/add?from=iteration&stepKey=${stage.field}`)}
    >{t(`${stage.label}.upload`)}</Button>
    : <Row gutter={20}>
      <Col flex={1}>
        <Button type='primary' disabled={!stage.trainValid} block onClick={goTraining}>
          <TrainIcon /> {t("project.iteration.stage.training")}
        </Button>
      </Col>
      <Col flex={1}>
        <Button block onClick={() => history.push(`/home/project/${pid}/model/import?from=iteration&stepKey=${stage.field}`)}>
          <ImportIcon /> {t("model.import.label")}
        </Button>
      </Col>
    </Row>

  return <Form.Item tooltip={t(stage.tip)} label={t(stage.label)}>
    <div>{!candidateList ? renderEmptyState(stage.type) : null}</div>
    <Form.Item
      hidden={!candidateList}
      name={stage.field}
      noStyle
      rules={[{ required: !stage.option }]}
      preserve={null}
    >
      <Selection pid={pid} changeByUser filters={filters} allowClear={!!stage.option} />
    </Form.Item>
    {runningDataset(result) ? <div className="state">{RenderProgress(result?.state, result, true)}</div> : null}
  </Form.Item>
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  return attr?.id ? attr.id : attr
}
