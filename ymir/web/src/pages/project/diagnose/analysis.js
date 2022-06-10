import React, { useEffect, useState } from "react"
import { Card, Button, Form, Row, Col, } from "antd"
import s from "./index.less"

import t from "@/utils/t"
import Panel from "@/components/form/panel"
import { CompareIcon } from "@/components/common/icons"

function Analysis() {
  const [form] = Form.useForm()

  const onFinish = async () => {
    // todo submit
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }


  // todo form initial values
  const initialValues = {}
  return (
    <div className={s.wrapper}>
      <Card className={s.container}>
        <Row gutter={20}>
          <Col span={18} style={{ border: '1px solid #ccc' }}>
            
          </Col>
          <Col span={6} className={s.formContainer}>
            <div className={s.mask} hidden={true}>
              <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}><CompareIcon /> {'restart'}</Button>
            </div>
            <Panel label={'Analysis'} style={{ marginTop: -10 }} toogleVisible={false}>
              <Form
                className={s.form}
                form={form}
                layout='vertical'
                name='labelForm'
                initialValues={initialValues}
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                labelAlign='left'
                colon={false}
              >
                <Form.Item name='submitBtn'>
                  <div style={{ textAlign: 'center' }}>
                    <Button type="primary" size="large" htmlType="submit">
                      <CompareIcon /> action
                    </Button>
                  </div>
                </Form.Item>
              </Form>
            </Panel>
          </Col>
        </Row>
      </Card>
    </div >
  )
}

export default Analysis
