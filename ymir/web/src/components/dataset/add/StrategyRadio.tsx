import { CheckboxOptionType, Radio, RadioGroupProps, Select, SelectProps } from 'antd'
import { FC, useState, useEffect } from 'react'
import { IMPORTSTRATEGY } from '@/constants/dataset'
import { useSelector } from 'umi'
import { Types } from './AddTypes'
import t from '@/utils/t'

type Props = Omit<SelectProps, 'options'> & { type: Types }
const prefix = 'dataset.add.label_strategy.'
const strategies: { value: string | number; label: string }[] = [
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD, label: t(`${prefix}add`) },
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: t(`${prefix}ignore`) },
  { value: IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE, label: t(`${prefix}exclude`) },
]

const StrategyRadio: FC<Props> = ({ type, ...rest }) => {
  const [options, setOptions] = useState<SelectProps['options']>([])

  useEffect(() => {
    let opts = strategies
    if (type === Types.COPY) {
      opts = strategies.filter((item) => item.value !== IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)
    } else if (type === Types.INTERNAL) {
      opts = []
    }
    setOptions(opts)
  }, [type])
  return <Select {...rest} defaultValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD} options={options} />
}
export default StrategyRadio
