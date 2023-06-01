import { Button, Form } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'

const SubmitBtn: FC = () => (
  <Form.Item label={' '}>
    <Button type="primary" htmlType="submit">
      {t('dataset.add.to.list')}
    </Button>
  </Form.Item>
)

export default SubmitBtn
