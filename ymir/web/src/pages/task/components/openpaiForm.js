import { Form, Radio } from "antd"
import t from '@/utils/t'
import { useEffect } from "react"

const types = [
  { value: false, label: 'task.train.device.local', checked: true, },
  { value: true, label: 'task.train.device.openpai', },
]

const OpenpaiForm = ({ form, openpai }) => {

  useEffect(() => {
    form.setFieldsValue({ openpai: openpai })
  }, [openpai])

  return openpai ? <Form.Item label={t('task.train.form.platform.label')} name='openpai' initialValue={false}>
  <Radio.Group options={types.map(type => ({ ...type, label: t(type.label) }))} />
</Form.Item> : null
}

export default OpenpaiForm
