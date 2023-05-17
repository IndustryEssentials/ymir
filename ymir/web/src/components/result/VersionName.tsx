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
    return id ? dataset.dataset[id] : undefined
  })
  const [dataset, setDataset] = useState<YModels.Result>()
  const [label, setLabel] = useState('')
  const [_, getDataset] = useFetch('dataset/getDataset')

  useEffect(() => id && getDataset({ id }), [id])

  useEffect(() => {
    setDataset(cache || result)
  }, [cache, result])

  useEffect(() => {
    dataset && setLabel(`${dataset.name} ${dataset.versionName}`)
  }, [dataset])

  return dataset ? (
    <span className="versionName">
      {label} {extra}
    </span>
  ) : null
}

export default VersionName
