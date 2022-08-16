import { Checkbox, Col, Form, Row } from "antd"
import { useEffect, useState } from "react"


const CheckboxSelector = ({ options = [], label = '', value, onChange = () => { }, vertical }) => {
  const [checkeds, setCheckeds] = useState([])

  useEffect(() => {
    value && setCheckeds(value)
  }, [value])

  useEffect(() => {
    onChange(checkeds)
  }, [checkeds])

  return <Row gutter={20}>
    <Col span={vertical ? 24 : null} style={{ fontWeight: 'bold' }}>{label}</Col>
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
