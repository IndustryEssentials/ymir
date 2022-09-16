import { useState, useEffect, useCallback } from "react"
import { useParams } from 'umi'
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"
import useFetch from '@/hooks/useFetch'
import { Button } from "antd"
import KeywordRates from "./keywordRates"

function SampleRates({ keywords, dataset, negative, progressWidth = 0.5 }) {
  const { id: pid } = useParams()
  const [did, setDid] = useState(null)
  const [kws, setKws] = useState([])
  const [stats, getNegativeKeywords, setStats] = useFetch('dataset/getNegativeKeywords', {})

  useEffect(() => {
    dataset?.id && setDid(dataset.id)
  }, [dataset])

  useEffect(() => {
    setStats({})
  }, [did, keywords])

  useEffect(() => {
    setKws(keywords)
  }, [keywords])

  useEffect(() => {
    const synced = kws?.length && did === dataset?.id && kws.every(k => keywords.includes(k))
    if (!negative && did && synced) {
      fetchKeywords(pid, kws, did)
    }
  }, [did, kws])

  function fetchKeywords(projectId, keywords, dataset) {
    getNegativeKeywords({ projectId, keywords, dataset })
  }

  return <div className={s.rates}>
    {negative && !list.gt.length ? <div>
      <Button type="primary"
        disabled={!did}
        onClick={() => fetchKeywords(pid, kws, did)}
      >
        {t('task.train.btn.calc.negative')}
      </Button>
    </div> : null}
    <KeywordRates title="Ground Truth" stats={stats.gt} progressWidth={progressWidth} />
    <KeywordRates title="Prediction" stats={stats.pred} progressWidth={progressWidth} />
  </div>
}

export default SampleRates
