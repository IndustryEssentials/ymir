import { useState, useEffect, useCallback } from "react"
import { useParams } from 'umi'
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"
import useFetch from '@/hooks/useFetch'
import { Button } from "antd"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

const initList = { gt: [], pred: [] }

const getWidth = ({ count = 0, max }, progressWidth) => percent(count * progressWidth / max)

function KeywordRates({ keywords, dataset, negative, progressWidth = 0.5 }) {
  const [list, setList] = useState(initList)
  const { id: pid } = useParams()
  const [did, setDid] = useState(null)
  const [kws, setKws] = useState([])
  const [stats, getNegativeKeywords, setStats] = useFetch('dataset/getNegativeKeywords', {})
  const [colors, setColors] = useState({})

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

  useEffect(() => {
    const keywordColors = (kws || []).reduce((prev, keyword) => (colors[keyword] ? prev : {
      ...prev,
      [keyword]: randomColor(),
    }), {
      0: 'gray'
    })
    setColors({ ...colors, ...keywordColors })
  }, [kws])

  useEffect(() => {
    if (stats.gt) {
      const list = generateList(stats, colors)
      setList(list)
    } else {
      setList(initList)
    }
  }, [stats, colors])

  function generateList({ gt, pred }, colors) {
    return {
      gt: transfer(gt, colors),
      pred: transfer(pred, colors),
    }
  }

  function fetchKeywords(projectId, keywords, dataset) {
    getNegativeKeywords({ projectId, keywords, dataset })
  }

  function transfer({ count = {}, keywords, negative = 0, total }, colors) {
    const klist = [
      ...(keywords.map(kw => ({
        key: kw,
        label: kw,
        count: count[kw],
      }))),
      {
        key: 0,
        label: t('dataset.samples.negative'),
        count: negative,
      }
    ]
    const max = Math.max(...(klist.map(item => item.count || 0)), progressWidth)
    return klist.map(item => ({
      ...item,
      total,
      max,
      color: colors[item.key],
    }))
  }

  function label({ count = 0, label = '', total }) {
    return `${label} ${count}/${total} ${percent(count / total)}`
  }

  const renderList = (list = [], title = 'Ground Truth') => list.length ? <div className={s.rates}>
    <div className={s.title}>{title}</div>
    {list.map(item => (
      <div key={item.key} className={s.rate}>
        <span className={s.bar} style={{ width: getWidth(item, progressWidth), background: item.color }}>&nbsp;</span>
        <span>{label(item)}</span>
      </div>
    ))}
  </div> : null

  return <div className={s.rates}>
    {negative && !list.gt.length ? <div>
      <Button type="primary"
        disabled={!did}
        onClick={() => fetchKeywords(pid, kws, did)}
      >
        {t('task.train.btn.calc.negative')}
      </Button>
    </div> : null}
    {renderList(list.gt)}
    {renderList(list.pred, 'Prediction')}
  </div>
}

export default KeywordRates
