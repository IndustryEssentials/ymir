import { useEffect } from "react"
import { useParams } from 'umi'
import t from "@/utils/t"

import useFetch from '@/hooks/useFetch'
import KeywordRates from "./KeywordRates"

function MiningSampleRates({ iid, progressWidth = 0.5 }) {
  const { id: pid } = useParams()
  const [stats, getMiningStats] = useFetch('iteration/getMiningStats', {}, true)

  useEffect(() => {
    iid && getMiningStats({ pid, id: iid })
  }, [iid])

  return <div>
    <KeywordRates title={t('project.iteration.mining.all.processed')} stats={stats.totalList} progressWidth={progressWidth} />
    <KeywordRates title={t('project.iteration.mining.keywords.processed')} stats={stats.keywordList} progressWidth={progressWidth} />
  </div>
}

export default MiningSampleRates
