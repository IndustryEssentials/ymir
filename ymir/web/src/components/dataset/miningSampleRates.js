import { useState, useEffect, useCallback } from "react"
import { useParams } from 'umi'
import t from "@/utils/t"

import useFetch from '@/hooks/useFetch'
import { Button } from "antd"
import KeywordRates from "./keywordRates"

function MiningSampleRates({ iid, progressWidth = 0.5 }) {
  const { id: pid } = useParams()
  const [stats, getMiningStats, setStats] = useFetch('iteration/getMiningStats', {}, true)

  useEffect(() => {
    iid && getMiningStats({ id: iid })
  }, [iid])

  useEffect(() => {
    setStats({})
  }, [did, keywords])


  useEffect(() => {
    const synced = keywords?.length && did === dataset?.id
    if (!negative && did && synced) {
      fetchKeywords(pid, keywords, did)
    }
  }, [did, keywords])

  function fetchKeywords(projectId, keywords, dataset) {
    getNegativeKeywords({ projectId, keywords, dataset })
  }

  return <div>
    <KeywordRates title="已挖掘数据占比" stats={stats.gt} progressWidth={progressWidth} />
    <KeywordRates title="已挖掘数据中正负样本占比" stats={stats.pred} progressWidth={progressWidth} />
  </div>
}

export default MiningSampleRates
