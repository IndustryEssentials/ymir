import { Button, Col, Form, FormItemProps, Input, message, Row } from 'antd'
import { FC, ReactNode } from 'react'
import t from '@/utils/t'
import { AddIcon, DeleteIcon } from '@/components/common/Icons'
import { formLayout } from '@/config/antd'
import SubmitBtn from './SubmitBtn'

type Props = {
  name: string
  rules?: FormItemProps['rules']
  tip?: ReactNode
  confirm: (items: string[]) => void
  max?: number
}
const Inputs: FC<Props> = ({ name, rules, tip = null, confirm, max = 0 }) => {
  const [form] = Form.useForm()
  const items = Form.useWatch(name, form)

  return (
    <Form
      name={`${name}Form`}
      form={form}
      {...formLayout}
      onFinish={(values) => {
        if (max > 0) {
          confirm(values[name])
          form.resetFields()
        } else {
          message.warning('Exceed Maximium Count')
        }
      }}
      onFinishFailed={(err) => {
        console.log('finish failed: ', err)
      }}
    >
      <Form.List name={name} initialValue={['']}>
        {(fields, { add, remove }) => (
          <>
            <Form.Item required label={t(`dataset.add.form.${name}.label`)}>
              {fields.map((field, index) => (
                <Row key={field.key}>
                  <Col flex={1}>
                    <Form.Item {...field} rules={rules}>
                      <Input placeholder={t(`dataset.add.form.${name}.placeholder`)} max={512} allowClear />
                    </Form.Item>
                  </Col>
                  <Col style={{ paddingLeft: '20px' }} flex={'100px'}>
                    {(!max || fields.length < max) && index === fields.length - 1 ? <AddIcon onClick={() => add()} /> : null}
                    {index > 0 ? <DeleteIcon onClick={() => remove(field.name)} /> : null}
                  </Col>
                </Row>
              ))}
              {tip}
            </Form.Item>
          </>
        )}
      </Form.List>
      <SubmitBtn disabled={!items?.filter((item: string) => !!item)?.length} />
    </Form>
  )
}

export default Inputs
