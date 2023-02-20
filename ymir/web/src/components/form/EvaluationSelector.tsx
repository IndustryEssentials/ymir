import { evaluationTags as tags } from '@/constants/dataset'
import type { RadioGroupProps } from 'antd'
import React from 'react'
import RadioGroup from './RadioGroup'

type Props = RadioGroupProps & {
  hidden?: boolean
}

const types = [
  { label: 'right', value: tags.mtp },
  { label: 'fn', value: tags.fn },
  { label: 'fp', value: tags.fp },
]

const EvaluationSelector: React.FC<Props> = (props) => (
  <RadioGroup optionType="button" {...props} prefix='dataset.assets.selector.evaluation.' options={types} />
)

export default EvaluationSelector
