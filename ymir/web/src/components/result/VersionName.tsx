import useFetch from '@/hooks/useFetch'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'umi'

type Props = {
  id?: YModels.DatasetId
  result?: YModels.Result
  extra?: React.ReactElement | string
}
const VersionName: React.FC<Props> = ({ id, result, extra }) => {
  const cache: YModels.Dataset = useSelector(({ dataset }: YStates.Root) => {
    return id && dataset.dataset[id]
  })
  const [dataset, setDataset] = useState<YModels.Result>()
  const [_, getDataset] = useFetch('dataset/getDataset')

  useEffect(() => id && getDataset({ id }), [id])

  useEffect(() => {
    setDataset(cache || result)
  }, [cache, result])

  const label = `${dataset?.name} ${dataset?.versionName}`
  return (
    <span className="versionName" title={label}>
      {label} {extra}
    </span>
  )
}

export default VersionName
