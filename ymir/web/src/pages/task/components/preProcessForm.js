import Panel from "@/components/form/panel"
import Tip from "@/components/form/tip"
import { Form, Input, InputNumber } from "antd"
import t from '@/utils/t'

const PreProcessForm = () => {
  return <Panel label={t('task.train.preprocess.title')} toogleVisible={false}>
    <Tip hidden={true}>
      <Form.Item name={['preprocess', 'longside_resize', 'dest_size']} label={t('task.train.preprocess.resize')}>
        <InputNumber step={1} max={10000} placeholder={t('task.train.preprocess.resize.placeholder')} />
      </Form.Item>
    </Tip>
  </Panel>
}

export default PreProcessForm
