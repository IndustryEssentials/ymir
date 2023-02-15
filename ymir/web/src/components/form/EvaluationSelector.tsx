import { evaluationTags as tags } from '@/constants/dataset'
import t from '@/utils/t'
import React from 'react'
import CheckboxSelector from './CheckboxSelector'
import RadioGroup from './RadioGroup'

type Props = YModels.PlainObject

const types = [
  { label: '预测正确', value: tags.mtp },
  { label: '预测错误-FN', value: tags.fn },
  { label: '预测错误-FP', value: tags.fp },
]

const EvaluationSelector: React.FC<Props> = (props) => (
  <RadioGroup options={types} {...props} optionType='button' />
)

export default EvaluationSelector
