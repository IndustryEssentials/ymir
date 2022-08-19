import { useState, useEffect } from "react"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

const initList = { gt: [], pred: [] }

const getWidth = ({ count = 0, max }, progressWidth) => percent(count * progressWidth / max)

function KeywordRates({ keywords, dataset, progressWidth = 0.5 }) {
  const [list, setList] = useState(initList)
  const [did, setDid] = useState(null)
  const [kws, setKws] = useState([])
  const [stats, getNegativeKeywords, setStats] = useFetch('dataset/getNegativeKeywords', {})
  const [colors, setColors] = useState({})

  useEffect(() => {
    dataset?.id && setDid(dataset.id)
  }, [dataset])

  useEffect(() => {
    setKws(keywords)
  }, [keywords])

  useEffect(() => {
    if (did && kws?.length && did === dataset.id && kws.every(k => keywords.includes(k))) {
      getNegativeKeywords({ keywords: kws, dataset: did })
    } else if (dataset?.id) {
      cacheToStats(dataset)
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

  function cacheToStats(dataset = {}) {
    const { gt, pred } = dataset
    setStats({ gt, pred })
  }

  const renderList = (list, title = 'Ground Truth') => <div className={s.rates}>
    <div className={s.title}>{title}</div>
    {list.map(item => (
      <div key={item.key} className={s.rate}>
        <span className={s.bar} style={{ width: getWidth(item, progressWidth), background: item.color }}>&nbsp;</span>
        <span>{label(item)}</span>
      </div>
    ))}
  </div>

  return (
    <div className={s.rates}>
      {renderList(list.gt)}
      {renderList(list.pred, 'Prediction')}
    </div>
  )
}

export default KeywordRates
