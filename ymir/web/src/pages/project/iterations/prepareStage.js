import { useCallback, useEffect, useMemo, useState } from "react"
import { Row, Col, Form } from "antd"

import t from '@/utils/t'
import { generateName } from '@/utils/string'
import useFetch from '@/hooks/useFetch'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'
import Uploader from '@/components/form/uploader'

import s from "./iteration.less"
import { YesIcon, LoaderIcon } from "@/components/common/icons"

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

export default function Stage({ pid, stage, form, project = {}, update }) {
  const [value, setValue] = useState(null)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])
  const [candidateList, setCandidateList] = useState(true)
  const [file, setFile] = useState({ name: '', url: '' })
  const [addResult, addDataset] = useFetch('dataset/createDataset')
  // const [updateResult, updateSettings] = useFetch('project/updateProject', null, true)

  useEffect(() => {
    setValid(value)
  }, [value])

  useEffect(() => {
    const value = getAttrFromProject(stage.field, project)
    setValue(value)
    setFieldValue(value)
  }, [stage, project])

  useEffect(() => {
    console.log('file:', file)
    file.url && addDataset({
      ...file,
      projectId: pid,
    })
  }, [file])

  useEffect(() => {
    if (addResult?.id) {
      update({[stage.field]: addResult.id })
    }
  }, [addResult])

  const setFieldValue = value => form.setFieldsValue({
    [stage.field]: value || null,
  })

  const renderIcon = () => {
    return valid ? <YesIcon /> : <LoaderIcon />
  }
  const renderState = () => {
    return valid ? t('project.stage.state.done') : t('project.stage.state.waiting')
  }

  const filters = stage.filter ? useCallback(datasets => {
    const result = stage.filter(datasets, project)
    console.log('result:', datasets, result, stage.field)
    setCandidateList(!!result.filter(item => item.assetCount).length)
    return result
  }, [stage.field, project]) : null

  return <Row wrap={false}>
    <Col>
      {!candidateList ? <Uploader
        onChange={(files, result) => { setFile({name: generateName(files[0].name), url: result}); console.log('files uploaded: ', files); }}
        max={1024}
        onRemove={() => setFile('')}
      /> : null}
      <Form.Item hidden={!candidateList} name={stage.field} label={t(stage.label)}
        tooltip={t(stage.tip)}
        rules={[{ required: !stage.option }]}
        preserve={null}
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
