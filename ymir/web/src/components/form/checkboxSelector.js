import { Checkbox, Col, Form, Row } from "antd"
import { forwardRef, useEffect, useImperativeHandle, useState } from "react"


const CheckboxSelector = forwardRef(({ options = [], label = '', value, onChange = () => { }, vertical }, ref) => {
  const [checkeds, setCheckeds] = useState([])
  const [clearable, setClearable] = useState(false)

  useImperativeHandle(ref, () => {
    return { clear }
  })

  function clear() {
    setClearable(true)
    setCheckeds([])
  }

  useEffect(() => {
    value && setCheckeds(value)
  }, [value])

  useEffect(() => {
    if (!clearable) {
      onChange(checkeds)
    }
    setClearable(false)
  }, [checkeds])

  return <Row gutter={20} ref={ref}>
    <Col span={vertical ? 24 : null} style={{ fontWeight: 'bold' }}>{label}</Col>
    <Col flex={1}>
      <Checkbox.Group
        value={checkeds}
        options={options}
        onChange={setCheckeds}
      />
    </Col>
  </Row>
})

export default CheckboxSelector
