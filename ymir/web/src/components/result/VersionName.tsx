import useFetch from '@/hooks/useFetch'
import React, { useEffect, useState } from 'react'
import { useSelector } from 'umi'

type Result = { name: string }
type Props = {
  id?: number
  result?: Result
  extra?: React.ReactElement | string
}

const VersionName: React.FC<Props> = ({ id, result: res, extra }) => {
  const cache: Result | undefined = useSelector(({ dataset }) => {
    return id ? dataset.dataset[id] : undefined
  })
  const [result, setResult] = useState<Result>()
  const [_, getDataset] = useFetch('dataset/getDataset')

  useEffect(() => id && getDataset({ id }), [id])

  useEffect(() => {
    setResult(cache || res)
  }, [cache, res])

  return result ? (
    <span className="versionName">
      {result.name} {extra}
    </span>
  ) : null
}

export default VersionName
