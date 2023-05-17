import { Checkbox, Form, InputNumber } from "antd"
import t from '@/utils/t'
import { useState } from "react"

const funcs = [
  {
    func: 'longside_resize',
    label: 'task.train.preprocess.resize',
    params: [{
      key: 'dest_size',
      rules: [{ required: true, message: t('task.train.preprocess.resize.placeholder'), }],
      component: <InputNumber step={1} min={1} max={10000} precision={0} placeholder={t('task.train.preprocess.resize.placeholder')} />
    }],
  }
]

const PreProcessForm = () => {
  const [selected, setSelected] = useState([])
  const renderTitle = (func, label) => <>
    <Checkbox style={{ marginRight: 10 }} value={func} checked={selected[func]} onChange={preprocessSelected} />
    {t(label)}
  </>
  function preprocessSelected({ target: { value, checked } }) {
    setSelected(old => ({ ...old, [value]: checked }))
  }
  return funcs.map(({ func, label, params }) =>
    <Form.Item key={func} label={renderTitle(func, label)} tooltip={t(`${label}.tip`)}>
      {selected[func] ? params.map(({ key, rules, component }) => (
        <Form.Item key={key} name={['preprocess', func, key]} rules={rules} noStyle>
          {component}
        </Form.Item>
      )) : null}
    </Form.Item>
  )
}

export default PreProcessForm
