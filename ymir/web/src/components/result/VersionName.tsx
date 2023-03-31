import useFetch from '@/hooks/useFetch'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'umi'

type Result = { name: string; versionName: string }
type Props = {
  id?: YModels.DatasetId
  result?: Result
  extra?: React.ReactElement | string
}

const VersionName: React.FC<Props> = ({ id, result, extra }) => {
  const cache: Result | undefined = useSelector(({ dataset }: YStates.Root) => {
    return id ? dataset.dataset[id] : undefined
  })
  const [dataset, setDataset] = useState<Result>()
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
