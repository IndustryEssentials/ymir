import { Col, InputNumber, Row, Slider } from 'antd'
import { SliderRangeProps, SliderSingleProps } from 'antd/lib/slider'
import { FC, useEffect, useState } from 'react'

type Props = Omit<SliderRangeProps, 'step' | 'value' | 'onChange' | 'range'> &
  SliderSingleProps & {
    step?: number
    hidden?: boolean
  }

const IouSlider: FC<Props> = ({ value = 0.5, onChange, hidden, min = 0.25, max = 0.95, step = 0.05, ...props }) => {
  const marks = [min, max].reduce<{ [key: number]: number }>((prev, curr) => ({ ...prev, [curr]: curr }), {})
  const [iou, setIou] = useState(value)

  useEffect(() => {
    value && setIou(value)
  }, [value])

  useEffect(() => {
    onChange && onChange(iou)
  }, [iou])

  function iouChange(iou: number) {
    const calIou = Math.min(Math.max(0.25, iou), 0.95)
    setIou(calIou)
  }

  return !hidden ? (
    <Row gutter={10}>
      <Col flex={1}>
        <Slider
          {...props}
          value={[iou, 1]}
          style={{ display: 'inline-block', width: '90%' }}
          range
          min={0}
          max={1}
          marks={marks}
          step={step}
          onChange={([iou]) => iouChange(iou)}
        />
      </Col>
      <Col>
        <InputNumber step={step} style={{ width: 60 }} value={iou} min={min} max={max} onChange={iouChange} />
      </Col>
    </Row>
  ) : null
}

export default IouSlider
