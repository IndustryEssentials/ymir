import { useCallback, useEffect, useMemo, useState } from 'react'
import { Row, Col, Form, Button, Select } from 'antd'
import { useHistory } from 'umi'

import { runningDataset } from '@/constants/dataset'
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'

import { AddIcon, TrainIcon, ImportIcon } from '@/components/common/Icons'
import RenderProgress from '@/components/common/Progress'

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

export default function Stage({ pid, stage, form, project = {}, result, trainValid, update }) {
  const history = useHistory()
  const [value, setValue] = useState(null)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])
  const [haveCandidateList, setHaveCandidateList] = useState(true)
  const [selectionList, setSelectionList] = useState([])

  useEffect(() => {
    setValid(value)
  }, [value])

  useEffect(() => {
    const value = getAttrFromProject(stage.field, project)
    setValue(value)
    setFieldValue(value)
  }, [stage, project])

  useEffect(() => {
    const candidateList = stage.filter(selectionList, project)
    const candidated = candidateList.length > 0
    setHaveCandidateList(candidated)
  }, [project, selectionList])

  const setFieldValue = (value) =>
    form.setFieldsValue({
      [stage.field]: value || null,
    })

  const goTraining = () => {
    const iparams = `from=iteration`
    history.push(`/home/project/${pid}/train?did=${project.candidateTrainSet}&test=${project.testSet.id}&${iparams}`)
  }

  const filters = stage.filter ? useCallback((datasets) => stage.filter(datasets, project), [stage.field, project]) : null

  const onSelectionReady = (list = []) => {
    setSelectionList(list)
  }

  const renderEmptyState = (type) =>
    !type ? (
      <Button type="primary" block icon={<AddIcon />} onClick={() => history.push(`/home/project/${pid}/dataset/add?from=iteration&stepKey=${stage.field}`)}>
        {t(`${stage.label}.upload`)}
      </Button>
    ) : (
      <Row gutter={20}>
        <Col flex={1}>
          <Button type="primary" disabled={!trainValid} block onClick={goTraining}>
            <TrainIcon /> {t('project.iteration.stage.training')}
          </Button>
        </Col>
        <Col flex={1}>
          <Button block onClick={() => history.push(`/home/project/${pid}/model/import?from=iteration&stepKey=${stage.field}`)}>
            <ImportIcon /> {t('model.import.label')}
          </Button>
        </Col>
      </Row>
    )

  const running = <Select disabled labelInValue value={`${result?.name} ${result?.versionName}`}></Select>

  return (
    <Form.Item tooltip={t(stage.tip)} label={t(stage.label)} required={!stage.option}>
      {runningDataset(result) ? (
        running
      ) : (
        <>
          <div>{!haveCandidateList && !project[stage.field] ? renderEmptyState(stage.type) : null}</div>
          <Form.Item hidden={!haveCandidateList && !project[stage.field]} name={stage.field} noStyle rules={[{ required: !stage.option }]} preserve={null}>
            <Selection pid={pid} changeByUser filters={filters} onReady={onSelectionReady} allowClear />
          </Form.Item>
        </>
      )}
      {runningDataset(result) ? <div className="state">{RenderProgress(result?.state, result, true)}</div> : null}
    </Form.Item>
  )
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  return attr?.id ? attr.id : attr
}
