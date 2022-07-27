import { Checkbox, Form } from "antd"
import { useEffect, useState } from "react"

const types = [
  {
    label: 'GT', value: 'gt', checked: true, children: [
      { label: 'FN', value: 'fn' },
      { label: 'MTP', value: 'mtp' },
    ]
  },
  {
    label: 'PRED', value: 'pred', children: [
      { label: 'FP', value: 'fp' },
      { label: 'TP', value: 'tp' },
    ]
  },
]

const GtSelector = ({ value, onChange = () => { }, ...props }) => {
  const [pcheckeds, setPCheckeds] = useState({
    gt: true,
    pred: true,
  })
  const [checkeds, setCheckeds] = useState({
    fn: true,
    fp: true,
    tp: true,
    mtp: true,
  })

  const [all, setAll] = useState({
    gt: false,
    pred: false,
  })

  useEffect(() => {
    onChange(checkeds)
  }, [checkeds])

  useEffect(() => {
    setPCheckeds({
      gt: checkeds.fn && checkeds.mtp,
      pred: checkeds.fp && checkeds.tp,
    })
    setAll({
      gt: (!checkeds.fn && checkeds.mtp) || (checkeds.fn && !checkeds.mtp),
      pred: (!checkeds.fp && checkeds.tp) || (checkeds.fp && !checkeds.tp),
    })
  }, [checkeds])

  function pChange({ target: { checked, value } }) {
    const { children } = types.find(type => type.value === value)
    setCheckeds(checkeds => ({
      ...checkeds,
      ...(children.reduce((prev, curr) => ({ ...prev, [curr.value]: checked }), {})),
    }))
  }

  function change(checked, list) {
    setCheckeds(checkeds => ({
      ...checkeds,
      ...(list.reduce((prev, curr) => ({ ...prev, [curr.value]: checked.includes(curr.value) }), {})),
    }))
  }

  return <Form colon={false} {...props}>
    {types.map(type => <Form.Item key={type.value} label={
      <Checkbox
        checked={pcheckeds[type.value]}
        value={type.value}
        onChange={pChange}
        indeterminate={all[type.value]}
      >
        {type.label} &gt;
      </Checkbox>}>
      <Checkbox.Group
        value={type.children.filter(item => checkeds[item.value]).map(({ value }) => value)}
        options={type.children}
        onChange={value => change(value, type.children)}
      />
    </Form.Item>)}
  </Form>
}

export default GtSelector
