import React from "react"

import AssetCount from '@/components/dataset/AssetCount'
import VersionName from '@/components/result/VersionName'
import { Dataset as DatasetType } from "@/interface/dataset"

type Props = { dataset: DatasetType }

const Dataset: React.FC<Props> = ({ dataset }) => {
  return dataset?.name ? <span>
  <VersionName result={dataset} /> (assets: <AssetCount dataset={dataset} />)
</span> : null
}

export default Dataset
