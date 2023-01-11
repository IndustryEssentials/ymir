import { Col, Form, FormInstance, Row } from 'antd'
import RadioGroup from '@/components/form/RadioGroup'
import t from '@/utils/t'
import type { FC, ReactChild } from 'react'

import { MergeType as Type } from '@/constants/dataset'
import DatasetName from '@/components/form/items/DatasetName'

const options = [
  { value: Type.New, label: 'new' },
  { value: Type.Exist, label: 'exist' },
]
type Props = {
  form: FormInstance
  existed?: ReactChild
  initialValue?: number
  disabledNew?: boolean
}
const MergeType: FC<Props> = ({ form, existed, initialValue = Type.Exist, disabledNew = false }) => {
  const type = Form.useWatch('type', form)

  const isNew = (type: Type) => type === Type.New

  return (
    <>
      <Row style={{ marginBottom: 20 }}>
        <Col offset={2}>
          <Form.Item name="type" initialValue={disabledNew ? Type.Exist : initialValue} noStyle>
            <RadioGroup
              optionType="button"
              buttonStyle="solid"
              options={options.map((option) => ({
                ...option,
                disabled: disabledNew && isNew(option.value),
              }))}
              prefix="task.merge.type."
            />
          </Form.Item>
        </Col>
      </Row>
      {isNew(type) ? <DatasetName /> : existed}
    </>
  )
}

export default MergeType
