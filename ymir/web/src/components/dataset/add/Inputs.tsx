import { Button, Col, Form, FormItemProps, Input, message, Row } from 'antd'
import { FC, ReactNode } from 'react'
import t from '@/utils/t'
import { AddIcon, DeleteIcon } from '@/components/common/Icons'
import { formLayout } from '@/config/antd'

type Props = {
  name: string
  rules?: FormItemProps['rules']
  tip?: ReactNode
  confirm: (items: string[]) => void
  max?: number
}
const Inputs: FC<Props> = ({ name, rules, tip = null, confirm, max = 0 }) => {
  const [form] = Form.useForm()

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
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Add to List
        </Button>
      </Form.Item>
    </Form>
  )
}

export default Inputs
