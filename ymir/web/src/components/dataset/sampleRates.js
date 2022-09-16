import { useState, useEffect, useCallback } from "react"
import { useParams } from 'umi'
import t from "@/utils/t"

import useFetch from '@/hooks/useFetch'
import { Button } from "antd"
import KeywordRates from "./keywordRates"

function SampleRates({ keywords, dataset, negative, progressWidth = 0.5 }) {
  const { id: pid } = useParams()
  const [did, setDid] = useState(null)
  const [stats, getNegativeKeywords, setStats] = useFetch('dataset/getNegativeKeywords', {}, true)

  useEffect(() => {
    dataset?.id && setDid(dataset.id)
  }, [dataset])

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
    {negative && !stats.gt ? <div>
      <Button type="primary"
        disabled={!did || !keywords?.length}
        onClick={() => fetchKeywords(pid, keywords, did)}
      >
        {t('task.train.btn.calc.negative')}
      </Button>
    </div> : null}
    <KeywordRates title="Ground Truth" stats={stats.gt} progressWidth={progressWidth} />
    <KeywordRates title="Prediction" stats={stats.pred} progressWidth={progressWidth} />
  </div>
}

export default SampleRates
