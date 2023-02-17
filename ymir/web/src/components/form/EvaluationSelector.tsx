import { evaluationTags as tags } from '@/constants/dataset'
import type { RadioGroupProps } from 'antd'
import React from 'react'
import RadioGroup from './RadioGroup'

type Props = RadioGroupProps & {
  hidden?: boolean
}

const types = [
  { label: '预测正确', value: tags.mtp },
  { label: '预测错误-FN', value: tags.fn },
  { label: '预测错误-FP', value: tags.fp },
]

const EvaluationSelector: React.FC<Props> = (props) => (
  <RadioGroup optionType='button' {...props} options={types} />
)

export default EvaluationSelector
