import React, { useEffect, useRef, useState } from "react"
import { Card, Button, Form, Row, Col, } from "antd"

import t from "@/utils/t"
import Panel from "@/components/form/panel"
import ModelSelect from "@/components/form/modelSelect"

import s from "./index.less"
import { CompareIcon } from "@/components/common/icons"
import { getTensorboardLink } from "../../../services/common"

function Training({ pid, project }) {
  const [form] = Form.useForm()
  const iframe = useRef(null)
  const [selectedModels, setSelectedModels] = useState([])
  const [tensorboardUrl, setUrl] = useState('')
  const [hasResult, setHasResult] = useState(false)

  useEffect(() => {
    if (iframe.current && tensorboardUrl) {
      console.log('iframe loaded')
      iframe.current.onload = () => {
        hideSidebar()
      }
    }
  }, [iframe.current, tensorboardUrl])

  const onFinish = async () => {
    let url = ''
    if (selectedModels.length) {
      const hashs = selectedModels.map(model => model.task.hash)
      url = getTensorboardLink(hashs)
    }
    setUrl(url)
    setHasResult(true)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function hideSidebar() {
    setTimeout(() => {
      try {
        console.log('iframe loaded')
        const document = iframe.current.contentWindow.document
        const sidebarShadowRoot = document.getElementsByTagName('tf-scalar-dashboard')[0].shadowRoot.children[1].shadowRoot

        var style = document.createElement('style')
        style.innerHTML = '#sidebar { display: none }'
        sidebarShadowRoot.appendChild(style)
      } catch (e) {
        hideSidebar()
      }
    }, 100)
  }

  function modelChange(id, options = []) {
    setSelectedModels(options.map(([{ model }]) => model) || [])
  }

  function retry() {
    setHasResult(false)
    setUrl('')
  }

  const initialValues = {}
  return (
    <div className={s.wrapper}>
      <Row gutter={20}>
        <Col span={18} style={{ border: '1px solid #ccc', minHeight: 500, height: 'calc(100vh - 300px)', padding: 0 }}>
          {tensorboardUrl ? <iframe ref={iframe} src={tensorboardUrl} style={{ width: '100%', height: '100%', border: 'none' }}></iframe>
            : ''}
        </Col>
        <Col span={6} className={s.formContainer}>
          <div className={s.mask} hidden={!hasResult}>
            <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}>
              <CompareIcon /> {t('model.action.diagnose.training.retry')}
            </Button>
          </div>
          <Panel label={'Training Fitting'} style={{ marginTop: -10 }} toogleVisible={false}>
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
              <Form.Item label={t('model.diagnose.form.model')} name='model' rules={[{ required: true }, { type: 'array', max: 5 }]}>
                <ModelSelect multiple placeholder={t('task.train.form.model.placeholder')} pid={pid} onChange={modelChange} />
              </Form.Item>
              <Form.Item name='submitBtn'>
                <div style={{ textAlign: 'center' }}>
                  <Button type="primary" size="large" htmlType="submit">
                    <CompareIcon /> {t('common.action.diagnose.training')}
                  </Button>
                </div>
              </Form.Item>
            </Form>
          </Panel>
        </Col>
      </Row>
    </div >
  )
}

export default Training
