import { FC, useEffect, useState } from 'react'
import t from '@/utils/t'
import { Col, Row, Select, SelectProps } from 'antd'
import V from './VisualModes'
import { BaseOptionType } from 'antd/lib/select'

type Props = SelectProps & {
  type?: string
}

const options = {
  [V.All]: { label: 'all' },
  [V.Asset]: { label: 'asset' },
  [V.Gt]: { label: 'gt' },
  [V.Pred]: { label: 'pred' },
  [V.GtPred]: { label: 'annotation' },
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
    <Row gutter={10}>
      <Col style={{ fontWeight: 'bold' }}>{t('dataset.assets.selector.visual.label')}</Col>
      <Col flex={1}>
        <Select
          {...props}
          defaultValue={opts[0].value}
          options={opts.map(({ value, label }) => ({ value, label: t(`dataset.assets.selector.visual.label.${label}`) }))}
        />
      </Col>
    </Row>
  ) : null
}

export default ListVisualSelect
