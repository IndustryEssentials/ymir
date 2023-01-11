import { useState, useEffect, FC } from 'react'
import { useParams } from 'umi'
import { useSelector } from 'react-redux'
import { Button } from 'antd'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import KeywordRates from './KeywordRates'
type Props = {
  keywords: string[]
  dataset?: YModels.Dataset
  negative?: boolean
  label?: string
  progressWidth?: number
}
const SampleRates: FC<Props> = ({ keywords, dataset, negative, label, progressWidth = 0.5 }) => {
  const { id: pid } = useParams<{ id: string }>()
  const [did, setDid] = useState(0)
  const effect = 'dataset/getNegativeKeywords'
  const [stats, getNegativeKeywords, setStats] = useFetch(effect, {}, true)
  const loading = useSelector<YStates.Root, boolean>(({ loading }) => loading.effects[effect])

  useEffect(() => {
    dataset?.id && setDid(dataset.id)
  }, [dataset])

  useEffect(() => {
    setStats({})
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

  useEffect(() => {
    const synced = keywords?.length && did === dataset?.id
    if (!negative && did && synced) {
      fetchKeywords(pid, keywords, did)
    }
  }, [did, keywords])

  function fetchKeywords(pid: string | number, keywords: string[] = [], did: number | null) {
    keywords.length && getNegativeKeywords({ pid, keywords, did })
  }

  return (
    <div>
      {label ? <h3 style={{ marginBottom: 10, fontWeight: 'bold' }}>{label}</h3> : null}
      {negative && !stats.gt ? (
        <div>
          <Button type="primary" disabled={!did || !keywords?.length} onClick={() => fetchKeywords(pid, keywords, did)} loading={loading}>
            {t('task.train.btn.calc.negative')}
          </Button>
        </div>
      ) : null}
      <KeywordRates title={t('annotation.gt')} stats={addNegativeInfo(stats.gt)} progressWidth={progressWidth} />
      <KeywordRates title={t('annotation.pred')} stats={addNegativeInfo(stats.pred)} progressWidth={progressWidth} />
    </div>
  )
}

export default SampleRates
