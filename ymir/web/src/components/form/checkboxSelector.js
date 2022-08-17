import { Checkbox, Col, Form, Row } from "antd"
import { useEffect, useState } from "react"


const CheckboxSelector = ({ options = [], label = '', value, onChange = () => { }, vertical }) => {
  const [checkeds, setCheckeds] = useState([])

  useEffect(() => {
    setCheckeds(value)
  }, [value])

  useEffect(() => {
    onChange(checkeds)
  }, [checkeds])

  return <Row gutter={20} ref={ref}>
    <Col span={vertical ? 24 : null} style={{ fontWeight: 'bold', textAlign: 'right' }}>{label}</Col>
    <Col flex={1}>
      <Checkbox.Group
        value={checkeds}
        options={options}
        onChange={setCheckeds}
      />
    </Col>
  </Row>
}

export default CheckboxSelector
