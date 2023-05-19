import { Form, FormItemProps, Input } from 'antd'
import { FC, ReactNode } from 'react'
import t from '@/utils/t'
import { AddIcon, DeleteIcon } from '@/components/common/Icons'
import { ImportSelectorProps } from '.'
import { Types } from './AddTypes'
type Props = {
  name: string
  rules?: FormItemProps['rules']
  tip?: ReactNode
  onChange: (items: string[]) => void
}
const Inputs: FC<Props> = ({ name, rules, tip, onChange }) => {
  const [form] = Form.useForm()
  return (
    <Form
      name={`${name}Form`}
      form={form}
      onValuesChange={(_, values) => {
        form
          .validateFields()
          .then(() => {
            onChange(values[name])
          })
          .catch(() => {})
      }}
    >
      <Form.List name={name} initialValue={['']}>
        {(fields, { add, remove }) => (
          <>
            <Form.Item label={t(`dataset.add.form.${name}.label`)}>
              {fields.map((field, index) => (
                <div key={field.key}>
                  <Form.Item {...field} noStyle rules={rules}>
                    <Input placeholder={t(`dataset.add.form.${name}.placeholder`)} max={512} allowClear />
                  </Form.Item>
                  {index === fields.length - 1 ? <AddIcon onClick={() => add()} /> : null}
                  {index > 1 ? <DeleteIcon onClick={() => remove(field.name)} /> : null}
                </div>
              ))}
              {tip ? <p>{tip}</p> : null}
            </Form.Item>
          </>
        )}
      </Form.List>
    </Form>
  )
}
export default Inputs
