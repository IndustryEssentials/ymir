import { FC, useEffect } from 'react'
import { useParams } from 'umi'
import t from '@/utils/t'
import useRequest from '@/hooks/useRequest'
import KeywordRates from './KeywordRates'

const MiningSampleRates: FC<{ iid: number; progressWidth?: number }> = ({ iid, progressWidth = 0.5 }) => {
  const { id: pid } = useParams<{ id: string }>()
  const { data: stats, run: getMiningStats } = useRequest<YModels.MiningStats, [{ pid: number | string; id: number }]>('iteration/getMiningStats', {
    loading: false,
  })

  useEffect(() => {
    iid && getMiningStats({ pid, id: iid })
  }, [iid])

  return stats ? (
    <div>
      <KeywordRates title={t('project.iteration.mining.all.processed')} stats={stats.totalList} progressWidth={progressWidth} />
      <KeywordRates title={t('project.iteration.mining.keywords.processed')} stats={stats.keywordList} progressWidth={progressWidth} />
    </div>
  ) : null
}

export default MiningSampleRates
