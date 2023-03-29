import { useState, useEffect, useRef, FC } from 'react'
import { Col, Form, Input, Row, Select } from 'antd'
import { percent } from '@/utils/number'
import useFetch from '@/hooks/useFetch'
import { BaseSelectRef } from 'rc-select'
import { BaseOptionType } from 'antd/lib/select'
const { useForm } = Form
type Props = {
  record: YModels.Model
  saveHandle?: (result: YModels.Model, updated: YModels.Model) => void
}
type OptionType = BaseOptionType & {
  stage: YModels.Stage
}
const EditStageCell: FC<Props> = ({ record, saveHandle = () => {} }) => {
  const [options, setOptions] = useState<OptionType[]>([])
  const [editing, setEditing] = useState(false)
  const selectRef = useRef<BaseSelectRef>(null)
  const [form] = useForm()
  const [result, setRecommendStage] = useFetch('model/setRecommendStage')
  const recommendStage = record?.stages?.find((stage) => stage.id === record.recommendStage)
  const multipleStages = record?.stages && record.stages.length > 1

  useEffect(() => {
    const options = record?.stages?.map((stage) => ({ stage, label: tagRender({ stage }), value: stage.id })) || []
    setOptions(options)
  }, [record])
  useEffect(() => {
    if (editing && multipleStages) {
      selectRef.current?.focus()
    }
  }, [editing])

  useEffect(() => {
    if (result) {
      saveHandle(result, record)
    }
  }, [result])

  const save = async () => {
    try {
      const values = await form.validateFields()
      await setRecommendStage({ ...values, model: record.id })
    } catch (errInfo) {
      console.log('Save failed:', errInfo)
    }
    setEditing(false)
  }

  const tagRender = ({ stage, color = 'rgba(0, 0, 0, 0.65)' }: { stage: YModels.Stage; color?: string }) => (
    <Row wrap={false}>
      <Col flex={1}>{stage.name}</Col>
      <Col style={{ color }}>
        {stage.primaryMetricLabel}: {percent(stage.primaryMetric)}
      </Col>
    </Row>
  )

  return editing && multipleStages ? (
    <Form form={form} initialValues={{ stage: record.recommendStage }} size={'small'}>
      <Form.Item
        style={{
          margin: 0,
        }}
        name="stage"
        rules={[{ required: true }]}
      >
        <Select ref={selectRef} onBlur={() => setEditing(false)} onChange={save} options={options}></Select>
      </Form.Item>
    </Form>
  ) : recommendStage ? (
    <div onMouseEnter={() => setEditing(true)} style={{ cursor: multipleStages ? 'pointer' : 'text' }}>
      {tagRender({ stage: recommendStage, color: 'orange' })}
    </div>
  ) : null
}

export default EditStageCell
