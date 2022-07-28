import { Checkbox, Form } from "antd"
import { useEffect, useState } from "react"
import { evaluationTags as tags } from '@/constants/dataset'

const types = [
  {
    label: 'GT', value: 'gt', checked: true, children: [
      { label: 'FN', value: tags.fn },
      { label: 'MTP', value: tags.mtp },
    ]
  },
  {
    label: 'PRED', value: 'pred', children: [
      { label: 'FP', value: tags.fp },
      { label: 'TP', value: tags.tp },
    ]
  },
]

const GtSelector = ({ value, onChange = () => { }, ...props }) => {
  const [pcheckeds, setPCheckeds] = useState({
    gt: true,
    pred: true,
  })
  const [checkeds, setCheckeds] = useState({
    [tags.fn]: true,
    [tags.fp]: true,
    [tags.tp]: true,
    [tags.mtp]: true,
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
      gt: checkeds[tags.fn] && checkeds[tags.mtp],
      pred: checkeds[tags.fp] && checkeds[tags.tp],
    })
    setAll({
      gt: (!checkeds[tags.fn] && checkeds[tags.mtp]) || (checkeds[tags.fn] && !checkeds[tags.mtp]),
      pred: (!checkeds[tags.fp] && checkeds[tags.tp]) || (checkeds[tags.fp] && !checkeds[tags.tp]),
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
