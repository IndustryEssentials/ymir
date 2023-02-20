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
  [V.All]: { label: 'all', },
  [V.Asset]: { label: 'asset', },
  [V.Gt]: { label: 'gt', },
  [V.Pred]: { label: 'pred', },
  [V.GtPred]: { label: 'annotation', },
}

const modes: { [key: string]: V[] } = {
  pred: [V.All, V.Gt, V.Pred, V.Asset],
  gt: [V.Gt, V.Asset],
}

const ListVisualSelect: FC<Props> = ({ type, ...props }) => {
  const [opts, setOpts] = useState<BaseOptionType[]>([])

  useEffect(() => {
    const opts = (modes[type || 'gt'] || modes['gt']).map((value) => ({
      value,
      ...options[value],
    }))

    setOpts(opts)
  }, [type])
  return opts.length ? (
    <Select
      {...props}
      defaultValue={opts[0].value}
      options={opts.map(({ value, label }) => ({ value, label: t(`dataset.assets.selector.visual.label.${label}`) }))}
    />
  ) : null
}

export default ListVisualSelect
