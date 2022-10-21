import Panel from "@/components/form/panel"
import { Button, Col, Form, Input, Row } from "antd"
import t from '@/utils/t'
import { getConfigUrl } from "./liveCodeConfig"
import { useEffect, useState } from "react"


const LiveCodeForm = ({ form, live }) => {
  const url = Form.useWatch(['live', 'git_url'], form)
  const id = Form.useWatch(['live', 'git_branch'], form)
  const config = Form.useWatch(['live', 'code_config'], form)
  const [configUrl, setConfigUrl] = useState('')

  useEffect(() => {
    if (url && id && config) {
      const configUrl = getConfigUrl({
        git_url: url,
        git_branch: id,
        code_config: config,
      })
      setConfigUrl(configUrl)
    } else {
      setConfigUrl('')
    }
  }, [url, id, config])

  return live ? <Panel label={t('task.train.live.title')} toogleVisible={false}>

    <Form.Item name={['live', 'git_url']} label={t('task.train.live.url')} rules={[
      { required: true }
    ]}>
      <Input placeholder={t('task.train.live.url.placeholder')} allowClear />
    </Form.Item>

    <Form.Item name={['live', 'git_branch']} label={t('task.train.live.id')} rules={[
      { required: true }
    ]}>
      <Input placeholder={t('task.train.live.id.placeholder')} allowClear />
    </Form.Item>

    <Form.Item label={t('task.train.live.config')}>
      <Row gutter={20}>
        <Col flex={1}>
          <Form.Item name={['live', 'code_config']} label={t('task.train.live.config')} noStyle rules={[
            { required: true }
          ]}>
            <Input placeholder={t('task.train.live.config.placeholder')} allowClear />
          </Form.Item>
        </Col>
        <Col hidden={!configUrl}><Button type="primary"><a href={configUrl} target='_blank'>{t('common.view')}</a></Button></Col>
      </Row>
    </Form.Item>
  </Panel> : null
}

export default LiveCodeForm
