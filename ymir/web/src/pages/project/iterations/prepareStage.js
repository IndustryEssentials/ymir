import { useEffect, useMemo, useState } from "react"
import { Row, Col, Form } from "antd"

import t from '@/utils/t'
import DatasetSelect from '@/components/form/datasetSelect'
import ModelSelect from '@/components/form/modelSelect'

import s from "./iteration.less"
import { YesIcon, LoaderIcon } from "@/components/common/icons"

const SettingsSelection = (Select) => {
  const Selection = (props) => {
    return <Select {...props} />
  }
  return Selection
}

export default function Stage({ pid, stage, form, project = {} }) {
  const [value, setValue] = useState(null)
  const [valid, setValid] = useState(false)
  const Selection = useMemo(() => SettingsSelection(stage.type ? ModelSelect : DatasetSelect), [stage.type])

  useEffect(() => {
    setValid(value)
  }, [value])

  useEffect(() => {
    const value = getAttrFromProject(stage.field, project)
    setValue(value)
    form.setFieldsValue({
      [stage.field]: value || null,
    })
  }, [stage, project])

  const renderIcon = () => {
    return valid ? <YesIcon /> : <LoaderIcon />
  }
  const renderState = () => {
    return valid ? t('project.stage.state.done') : t('project.stage.state.waiting')
  }

  const filters = stage.filter ? datasets => stage.filter(datasets, project) : null

  return <Row wrap={false}>
    <Col flex={'60px'}>
      <div className={s.state}>{renderIcon()}</div>
      <div className={s.state}>{renderState()}</div>
    </Col>
    <Col flex={1}>
      <Form.Item name={stage.field} label={t(stage.label)}
        tooltip={t(stage.tip)}
        rules={[{ required: !stage.option }]}
      >
        <Selection value={value} pid={pid} changeByUser filters={filters} allowClear={!!stage.option} />
      </Form.Item>
    </Col>
  </Row>
}

function getAttrFromProject(field, project = {}) {
  const attr = project[field]
  return attr?.id ? attr.id : attr
}
