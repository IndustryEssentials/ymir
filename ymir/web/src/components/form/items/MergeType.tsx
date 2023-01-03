import { Form, FormInstance } from 'antd'
import RadioGroup from '@/components/form/RadioGroup'
import t from '@/utils/t'
import { FC, ReactChild } from 'react'

import DatasetName from '@/components/form/items/DatasetName'

const options = [
  { value: 0, label: 'new' },
  { value: 1, label: 'exist' },
]
type Props = {
  initialValue: number
  disabled: number[],
  form: FormInstance,
  existed?: ReactChild,
}
const MergeType: FC<Props> = ({ form, existed, initialValue = 0, disabled = [] }) => {
  const type = Form.useWatch('type', form)

  return (
    <>
      <Form.Item name="type" initialValue={initialValue} label={t('task.merge.type.label')}>
        <RadioGroup
          options={options.map((option) => ({
            ...option,
            disabled: disabled.includes(option.value),
          }))}
          prefix="task.merge.type."
        />
      </Form.Item>
      {!type ? <DatasetName /> : existed}
    </>
  )
}

export default MergeType
