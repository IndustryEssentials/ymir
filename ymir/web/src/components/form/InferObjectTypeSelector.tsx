import { Form, Radio, RadioGroupProps } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'

export enum Types {
  All,
  TrainingTarget,
}

const InferObjectTypeSelector: FC<RadioGroupProps> = (props) => {
  const options = [
    { value: Types.All, label: t('task.infer.objectType.all') },
    { value: Types.TrainingTarget, label: t('task.infer.objectType.trainingTarget') },
  ]
  return (
    <Form.Item name="objectType" label={t('task.infer.objectType.label')} initialValue={Types.TrainingTarget}>
      <Radio.Group {...props} options={options}></Radio.Group>
    </Form.Item>
  )
}
export default InferObjectTypeSelector
