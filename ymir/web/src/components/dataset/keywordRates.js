import { useState, useEffect } from "react"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ pid, id, keywords = [], dataset, progressWidth = 0.5 }) {
  const [list, setList] = useState([])
  const [stats, getNegativeKeywords, setStats] = useFetch('dataset/getNegativeKeywords', {})
  const [colors, setColors] = useState({})
  const [labels, setLabels] = useState([])

  useEffect(() => {
    if (dataset) {
      setLabels(dataset.keywords)
    } else if (keywords.length) {
      setLabels(keywords)
    } else {
      setLabels([])
    }
  }, [keywords, dataset])

  useEffect(() => {
    if (!dataset && id && labels?.length) {
      getNegativeKeywords({ projectId: pid, keywords: labels, dataset: id })
    } else if (dataset) {
      cacheToStats()
    } else {
      setList([])
    }
  }, [id, dataset, labels])

  useEffect(() => {
    const keywordColors = labels.reduce((prev, keyword) => (colors[keyword] ? prev : {
      ...prev,
      [keyword]: randomColor(),
    }), {
      0: 'gray'
    })
    setColors({ ...colors, ...keywordColors })
  }, [labels])

  useEffect(() => {
    if (typeof stats.negative !== 'undefined') {
      const list = generateList(stats)
      setList(list)
    } else {
      setList([])
    }
  }, [stats])

  function generateList(stats) {
    const total = stats.negative + stats.positive
    const klist = [
      ...(labels.map(keyword => ({
        key: keyword,
        label: keyword,
        count: stats.keywords[keyword],
      }))),
      {
        key: 0,
        label: t('dataset.samples.negative'),
        count: stats.negative,
      }]
    const max = Math.max(...(klist.map(item => item.count || 0)))
    return klist.map(item => ({
      ...item,
      total,
      max,
      color: colors[item.key],
    }))
  }
  const getWidth = ({ count = 0, max }) => percent(count * progressWidth / max)

  function label({ count = 0, label = '', total }) {
    return `${label} ${count}/${total} ${percent(count / total)}`
  }

  function cacheToStats() {
    const { assetCount, keywordsCount, nagetiveCount, } = dataset
    const defaultStats = {
      keywords: keywordsCount,
      negative: nagetiveCount,
      positive: assetCount - nagetiveCount,
      total: assetCount,
    }
    setStats(defaultStats)
  }

  return (
    <div className={s.rates}>
      {list.map(item => (
        <div key={item.key} className={s.rate}>
          <span className={s.bar} style={{ width: getWidth(item), background: item.color }}>&nbsp;</span>
          <span>{label(item)}</span>
        </div>
      ))}
    </div>
  )
}

export default KeywordRates
