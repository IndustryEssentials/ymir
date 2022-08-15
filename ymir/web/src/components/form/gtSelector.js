import { Checkbox, Form } from "antd"
import { useEffect, useState } from "react"
import { evaluationTags as tags } from '@/constants/dataset'

const types = [
  {
    label: 'GT', value: 'gt', checked: true, children: [
      { label: 'FN', value: tags.fn },
      { label: 'MTP', value: tags.mtp },
      { label: 'Other', value: tags.gto },
    ]
  },
  {
    label: 'PRED', value: 'pred', children: [
      { label: 'FP', value: tags.fp },
      { label: 'TP', value: tags.tp },
      { label: 'Other', value: tags.predo },
    ]
  },
]

const GtSelector = ({ value, onChange = () => { }, ...props }) => {
  const [pcheckeds, setPCheckeds] = useState({
    gt: false,
    pred: false,
  })
  const [checkeds, setCheckeds] = useState({
    gt: [],
    pred: [],
  })

  const [all, setAll] = useState({
    gt: false,
    pred: false,
  })

  useEffect(() => {
    onChange(checkeds)
  }, [checkeds])

  useEffect(() => {
    setAll(types.reduce((prev, { value }) => ({
      ...prev, [value]:
        [1, 2].includes(checkeds[value].length)
    }), {}))
  }, [checkeds])

  function pChange({ target: { checked, value } }) {
    const parent = types.find(type => type.value === value)
    setPCheckeds(checkeds => ({
      ...checkeds,
      [value]: checked,
    }))
    setCheckeds(checkeds => ({
      ...checkeds,
      [value]: checked ? parent.children.map(item => item.value) : [],
    }))
  }

  function change(checked, type) {
    setCheckeds(checkeds => ({
      ...checkeds,
      [type]: checked,
    }))
    setPCheckeds(checkeds => ({
      ...checkeds,
      [type]: checked.length !== 0,
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
        value={checkeds[type.value]}
        options={type.children}
        onChange={value => change(value, type.value)}
      />
    </Form.Item>)}
  </Form>
}

export default GtSelector
