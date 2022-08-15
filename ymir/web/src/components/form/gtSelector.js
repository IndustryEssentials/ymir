import t from "@/utils/t"
import CheckboxSelector from "./checkboxSelector"

const types = [
  { label: 'GT', value: 'gt', checked: true, },
  { label: 'PRED', value: 'pred', },
]

const GtSelector = (props) => <CheckboxSelector
  options={types}
  label={t('dataset.assets.selector.gt.label')}
  {...props}
/>

export default GtSelector
