import { useState, useEffect, FC } from "react"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"
type StatType = {
    keywords: string[],
    count?: { [key: string]: number},
    negative?: number,
    total?: number
  }
type Props = {
  stats?: StatType,
  title?: string
  progressWidth?: number
}

type ItemType = {
  key: string
label: string
count: number
total: number
max: number
color: string
}

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

const getWidth = ({ count = 0, max = 1 }, progressWidth: number) => percent(count * progressWidth / max)

// type stats = { count = {}, keywords, negative = 0, total }
const KeywordRates: FC<Props> = ({ title = '', stats, progressWidth = 0.5 }) => {
  const [list, setList] = useState<ItemType[]>([])
  const [keywords, setKws] = useState<string[]>([])
  const [colors, setColors] = useState<{ [key: string]: string}>({})

  useEffect(() => {
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
    setList(keywords.length && stats ? generateList(stats) : [])
  }, [stats, colors])


  function generateList({ count = {}, keywords = [], negative = 0, total }: StatType) {
    const klist = [
      ...(keywords.map(kw => ({
        key: kw,
        label: kw,
        count: count[kw],
        total: total ? total : count[kw + '_total'],
      }))),
    ]
    const max = Math.max(...(klist.map(item => item.count || 0)), progressWidth)
    return klist.map(item => ({
      ...item,
      max,
      color: colors[item.key],
    }))
  }

  function label({ count = 0, label = '', total }: ItemType) {
    const countLabel = total ? count / total : 0
    return `${label} ${count}/${total} ${percent(countLabel)}`
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
