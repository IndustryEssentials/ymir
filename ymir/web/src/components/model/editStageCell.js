import { useState, useEffect, useRef } from "react"
import { Form, Input, Select } from "antd"
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
      form.setFieldsValue({
        'stage': record.recommendStage,
      })
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

  return editing && multipleStages ? (
    <Form form={form} initialValues={{ stage: record.recommendStage }} size={'small'}>
      <Form.Item
        style={{
          margin: 0,
        }}
        name='stage'
        rules={[
          {
            required: true,
          },
        ]}
      >
        <Select ref={selectRef}
          onBlur={() => setEditing(false)}
          onChange={save}
          options={record?.stages?.map(stage => ({ label: `${stage.name} ${percent(stage.map)}`, value: stage.id }))}
        ></Select>
      </Form.Item>
    </Form>
  ) : (
    <div
      onMouseEnter={() => setEditing(true)}
      style={{ cursor: multipleStages ? 'pointer' : 'text' }}
    >
      {recommendStage.name} {percent(recommendStage.map)}
    </div>
  )
}

export default EditStageCell
