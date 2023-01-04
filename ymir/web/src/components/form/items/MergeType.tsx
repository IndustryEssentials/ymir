import { Form, FormInstance } from 'antd'
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
  initialValue: number
  disabled: number[],
  form: FormInstance,
  existed?: ReactChild,
}
const MergeType: FC<Props> = ({ form, existed, initialValue = Type.Exist, disabled = [] }) => {
  const type = Form.useWatch('type', form)

  const isNew = (type: number) => type === Type.New

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
      {isNew(type) ? <DatasetName /> : existed}
    </>
  )
}

export default MergeType
