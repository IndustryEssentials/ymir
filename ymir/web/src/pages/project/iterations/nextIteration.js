import { Col, Form, Row } from "antd"

export default function NextIteration({ok = () => {}, bottom}) {
  const [form] = Form.useForm()

  return <Form form={form} onFinish={ok}>
    <Row justify="center"><Col>{bottom}</Col></Row>
  </Form>
}