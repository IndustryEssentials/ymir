import { useState, useEffect, FC } from 'react'
import { useParams } from 'umi'

import t from '@/utils/t'
import KeywordRates from './KeywordRates'
import useRequest from '@/hooks/useRequest'

type Props = {
  keywords: string[]
  dataset?: YModels.Dataset
  label?: string
  progressWidth?: number
}

const SampleRates: FC<Props> = ({ keywords, dataset, label, progressWidth = 0.5 }) => {
  const { id } = useParams<{ id: string }>()
  const pid = Number(id)
  const [did, setDid] = useState(0)
  const {
    data: stats,
    run: getNegativeKeywords,
  } = useRequest<YModels.AnnotationsCount, [YParams.DatasetQuery]>('dataset/getNegativeKeywords', {
    loading: false,
  })

  useEffect(() => {
    dataset?.id && setDid(dataset.id)
  }, [dataset])

  useEffect(() => {
    fetchKeywords(pid, keywords, did)
  }, [did, keywords])

  const addNegativeInfo = (stat: { keywords?: string[]; count?: { [key: string]: number }; negative?: number } = {}) => {
    if (!stat?.keywords?.length) {
      return
    }
    const key = t('dataset.samples.negative')
    return {
      ...stat,
      keywords: [...stat.keywords, key],
      count: {
        ...stat.count,
        [key]: stat.negative,
      },
    }
  }

  function fetchKeywords(pid: number, keywords: string[] = [], did: number) {
    keywords.length && did && getNegativeKeywords({ pid, keywords, did })
  }

  return (
    <div>
      {label ? <h3 style={{ marginBottom: 10, fontWeight: 'bold' }}>{label}</h3> : null}
      <KeywordRates stats={addNegativeInfo(stats)} progressWidth={progressWidth} />
    </div>
  )
}

export default SampleRates
