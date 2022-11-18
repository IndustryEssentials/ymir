import { Checkbox, CheckboxOptionType, Col, Form, Row } from "antd"
import { CheckboxValueType } from "antd/lib/checkbox/Group"
import React, {useEffect, useState } from "react"
import type CSS from "csstype"

type Props = {
  options: CheckboxOptionType[],
  label?: string,
  value?: string[],
  onChange?: Function,
  vertical?: boolean,
  labelAlign?: CSS.Property.TextAlign,
}

const CheckboxSelector: React.FC<Props> = ({ options = [], label = '', value, onChange, vertical, labelAlign = 'left', ...rest }) => {
  const [checkeds, setCheckeds] = useState<CheckboxValueType[]>([])

  useEffect(() => value && setCheckeds(value), [value])

  useEffect(() => onChange && onChange(checkeds), [checkeds])

  return <Row gutter={20} {...rest}>
    <Col span={vertical ? 24 : undefined} style={{ fontWeight: 'bold', textAlign: labelAlign }}>{label}</Col>
    <Col flex={1}>
      <Checkbox.Group
        value={checkeds}
        options={options}
        onChange={(value) =>setCheckeds(value)}
      />
    </Col>
  </Row>
}

export default CheckboxSelector
