import { evaluationTags as tags } from '@/constants/dataset'
import t from '@/utils/t'
import React from 'react'
import CheckboxSelector from './CheckboxSelector'

type Props = YModels.PlainObject

const types = [
  { label: 'FN', value: tags.fn },
  { label: 'MTP', value: tags.mtp },
  { label: 'FP', value: tags.fp },
  { label: 'TP', value: tags.tp },
]

const EvaluationSelector: React.FC<Props> = (props) => (
  <CheckboxSelector options={types} label={t('dataset.assets.selector.evaluation.label')} checkedDefault={true} {...props} />
)

export default EvaluationSelector
