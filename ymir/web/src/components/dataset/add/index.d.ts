import { TASKTYPES } from '@/constants/task'
import { Types } from './AddTypes'

type ImportItem = {
  type: Types
  name: string
  source: string
  sourceName: string
}

type ImportSelectorChange = (items: ImportItem[]) => void
type ImportSelectorProps = {
  onChange: ImportSelectorChange
}

export { ImportItem, ImportSelectorChange, ImportSelectorProps }
