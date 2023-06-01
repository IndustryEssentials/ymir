import { ImportingItem } from '@/constants'

type ImportSelectorChange = (items: ImportingItem[]) => void
type ImportSelectorProps = {
  confirm: ImportSelectorChange
  max: number
}

export { ImportSelectorChange, ImportSelectorProps }
