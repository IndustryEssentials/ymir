import { Button, ButtonProps, Form } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'

const SubmitBtn: FC<ButtonProps> = (props) => (
  <Form.Item label={' '}>
    <Button type="primary" {...props} htmlType="submit">
      {t('dataset.add.to.list')}
    </Button>
  </Form.Item>
)

export default SubmitBtn
