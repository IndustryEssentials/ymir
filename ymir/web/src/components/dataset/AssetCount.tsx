import { humanize } from '@/utils/number'
import React from 'react'

type Props = { dataset: YModels.Dataset }

const AssetCount: React.FC<Props> = ({ dataset }) => {
  const count = dataset?.assetCount
  return <span title={`${count}`}>{humanize(count)}</span>
}

export default AssetCount
