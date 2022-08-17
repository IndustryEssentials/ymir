import { Checkbox, Col, Form, Row } from "antd"
import { useEffect, useState } from "react"


const CheckboxSelector = ({ options = [], label = '', value, onChange = () => { }, vertical, labelAlign, ...rest }) => {
  console.log('labelAlign:', labelAlign)
  const [checkeds, setCheckeds] = useState([])

  useEffect(() => {
    setCheckeds(value)
  }, [value])

  useEffect(() => {
    onChange(checkeds)
  }, [checkeds])

  return <Row gutter={20} {...rest}>
    <Col span={vertical ? 24 : null} style={{ fontWeight: 'bold', textAlign: labelAlign || 'left' }}>{label}</Col>
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
