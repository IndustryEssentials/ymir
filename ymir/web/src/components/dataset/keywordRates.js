import { useState, useEffect } from "react"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

const getWidth = ({ count = 0, max }, progressWidth) => percent(count * progressWidth / max)

function KeywordRates({ title = '', stats, progressWidth = 0.5 }) {
  const [list, setList] = useState([])
  const [keywords, setKws] = useState([])
  const [colors, setColors] = useState({})

  useEffect(() => {
    console.log('stats:', stats)
    const kws = stats?.keywords || []
    setKws(kws)
  }, [stats])

  useEffect(() => {
    const keywordColors = (keywords || []).reduce((prev, keyword) => (colors[keyword] ? prev : {
      ...prev,
      [keyword]: randomColor(),
    }), {
      0: 'gray'
    })
    setColors({ ...colors, ...keywordColors })
  }, [keywords])

  useEffect(() => {
    setList(keywords.length && stats ? generateList(stats, colors) : [])
  }, [stats, colors])


  function generateList({ count = {}, keywords, negative = 0, total }, colors) {
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
  return list.length ? <div className={s.rates}>
    <div className={s.title}>{title}</div>
    {list.map(item => (
      <div key={item.key} className={s.rate}>
        <span className={s.bar} style={{ width: getWidth(item, progressWidth), background: item.color }}>&nbsp;</span>
        <span>{label(item)}</span>
      </div>
    ))}
  </div> : null
}

export default KeywordRates
