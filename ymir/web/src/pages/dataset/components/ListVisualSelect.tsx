import { FC, useEffect, useState } from 'react'
import t from '@/utils/t'
import { Select, SelectProps } from 'antd'
import V from './VisualModes'
import { BaseOptionType } from 'antd/lib/select'

type optionType = 1 | 3 | 7
type Props = SelectProps & {
  type?: string
  actualClasses?: optionType[]
}

const options = {
  [V.All]: { label: 'all', allowed: 11 },
  [V.Asset]: { label: 'asset', allowed: 1 },
  [V.Gt]: { label: 'gt', allowed: 4 },
  [V.Pred]: { label: 'pred', allowed: 8 },
  [V.GtPred]: { label: 'annotation', allowed: 10 },
}

const modes: { [key: string]: V[] } = {
  pred: [V.All, V.Gt, V.Pred, V.Asset],
  gt: [V.Gt, V.Asset],
}

const ListVisualSelect: FC<Props> = ({ type = 'gt', actualClasses = [], ...props }) => {
  const [opts, setOpts] = useState<BaseOptionType[]>([])

  useEffect(() => {
    const opts = (modes[type] || modes['gt'])
      .map((value) => ({
        value,
        ...options[value],
      }))
      // .filter((option) => option.allowed === actualClasses.reduce((prev, current) => prev + current, 0))

    setOpts(opts)
  }, [type, actualClasses])
  return <Select {...props} options={opts.map(({ value, label }) => ({ value, label: t(`dataset.assets.selector.visual.label.${label}`) }))} />
}

export default ListVisualSelect
