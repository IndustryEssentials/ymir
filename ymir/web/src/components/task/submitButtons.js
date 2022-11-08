import { Button, Form, Space } from "antd"
import { useHistory } from "umi"

import t from "@/utils/t"

const SubmitButtons = ({ label = 'common.confirm' }) => {
  const history = useHistory()
  return <Space size={20}><Form.Item name='submitBtn' noStyle>
    <Button type="primary" size="large" htmlType="submit">
      {t(label)}
    </Button>
  </Form.Item>
    <Form.Item name='backBtn' noStyle>
      <Button size="large" onClick={() => history.goBack()}>
        {t('task.btn.back')}
      </Button>
    </Form.Item>
  </Space>
}

export default SubmitButtons
