import { Form, Radio } from "antd"
import t from '@/utils/t'
import { useEffect } from "react"

const types = [
  { value: true, label: 'common.yes', },
  { value: false, label: 'common.no', checked: true, },
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
