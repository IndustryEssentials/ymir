import { evaluationTags as tags } from '@/constants/dataset'
import type { RadioGroupProps } from 'antd'
import React from 'react'
import t from '@/utils/t'
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
  <RadioGroup optionType="button" {...props} options={types.map(({ value, label }) => ({ value, label: t(`dataset.assets.selector.evaluation.${label}`) }))} />
)

export default EvaluationSelector
