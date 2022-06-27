import Panel from "@/components/form/panel"
import Tip from "@/components/form/tip"
import { Form, Input } from "antd"
import t from '@/utils/t'

const LiveCodeForm = ({ live }) => {
  return live ? <Panel label={t('task.train.live.title')} toogleVisible={false}>
    <Tip hidden={true}>
      <Form.Item name={['live', 'git_url']} label={t('task.train.live.url')} rules={[
        { required: true }
      ]}>
        <Input placeholder={t('task.train.live.url.placeholder')} /></Form.Item>
    </Tip>
    <Tip hidden={true}>
      <Form.Item name={['live', 'git_branch']} label={t('task.train.live.id')} rules={[
        { required: true }
      ]}>
        <Input placeholder={t('task.train.live.id.placeholder')} /></Form.Item>
    </Tip>
    <Tip hidden={true}>
      <Form.Item name={['live', 'code_config']} label={t('task.train.live.config')} rules={[
        { required: true }
      ]}>
        <Input placeholder={t('task.train.live.config.placeholder')} /></Form.Item>
    </Tip>
  </Panel> : null
}

export default LiveCodeForm
