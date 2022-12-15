import React from 'react'

import AssetCount from '@/components/dataset/AssetCount'
import VersionName from '@/components/result/VersionName'

type Props = { dataset: YModels.Dataset }

const Dataset: React.FC<Props> = ({ dataset }) => {
  return dataset?.name ? (
    <span>
      <VersionName result={dataset} /> (assets: <AssetCount dataset={dataset} />)
    </span>
  ) : null
}

export default Dataset
