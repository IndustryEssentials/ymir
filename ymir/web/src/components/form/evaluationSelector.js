import { evaluationTags as tags } from '@/constants/dataset'
import t from "@/utils/t"
import { forwardRef } from 'react'
import CheckboxSelector from "./checkboxSelector"

const types = [
  { label: 'FN', value: tags.fn },
  { label: 'MTP', value: tags.mtp },
  { label: 'FP', value: tags.fp },
  { label: 'TP', value: tags.tp },
]

const EvaluationSelector = forwardRef((props, ref) => <CheckboxSelector
  options={types}
  label={t('dataset.assets.selector.evaluation.label')}
  ref={ref}
  {...props}
/>)

export default EvaluationSelector
