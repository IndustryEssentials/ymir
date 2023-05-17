import { useState, useEffect, useRef } from "react"
import { Col, Form, Input, Row, Select } from "antd"
import t from '@/utils/t'
import { percent } from '@/utils/number'
import useFetch from '@/hooks/useFetch'
const { useForm } = Form

const EditStageCell = ({ record, saveHandle = () => { } }) => {
  const [editing, setEditing] = useState(false)
  const selectRef = useRef(null)
  const [form] = useForm()
  const [result, setRecommendStage] = useFetch('model/setRecommendStage')
  const recommendStage = record.stages.find(stage => stage.id === record.recommendStage) || {}
  const multipleStages = record.stages.length > 1

  useEffect(() => {
    if (editing && multipleStages) {
      selectRef.current.focus()
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

  const tagRender = ({ stage, color = 'rgba(0, 0, 0, 0.65)' }) => (<Row wrap={false}>
    <Col flex={1}>{stage.name}</Col>
    <Col style={{ color }}>{stage.primaryMetricLabel}: {percent(stage.primaryMetric)}</Col>
  </Row>)

  return editing && multipleStages ? (
    <Form form={form} initialValues={{ stage: record.recommendStage }} size={'small'}>
      <Form.Item
        style={{
          margin: 0,
        }}
        name='stage'
        rules={[
          { required: true, },
        ]}
      >
        <Select ref={selectRef}
          onBlur={() => setEditing(false)}
          onChange={save}
          options={record?.stages?.map(stage => ({ stage, label: tagRender({ stage }), value: stage.id }))}
          tagRender={tagRender}
        ></Select>
      </Form.Item>
    </Form>
  ) : (
    <div
      onMouseEnter={() => setEditing(true)}
      style={{ cursor: multipleStages ? 'pointer' : 'text' }}
    >
      {tagRender({ stage: recommendStage, color: 'orange' })}
    </div>
  )
}

export default EditStageCell
