import t from "@/utils/t"
import { forwardRef } from "react"
import CheckboxSelector from "./checkboxSelector"

const types = [
  { label: 'GT', value: 'gt', checked: true, },
  { label: 'PRED', value: 'pred', },
]

const GtSelector = forwardRef((props, ref) => <CheckboxSelector
  options={types}
  label={t('dataset.assets.selector.gt.label')}
  ref={ref}
  {...props}
/>)

export default GtSelector
