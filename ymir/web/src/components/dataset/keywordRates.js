import { useState, useEffect } from "react"
import { Row, Col, Progress, } from "antd"
import { connect } from 'dva'
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ id, dataset = {}, progressWidth = 0.8, getKeywordRates }) {
  const [data, setData] = useState(null)
  const [list, setList] = useState([])

  useEffect(() => {
    if (dataset.id) {
      setData(dataset)
    } else {
      id && fetchRates()
    }
  }, [id])

  useEffect(() => {
    if (data) {
      const klist = prepareList(data)
      setList(klist)
    }
  }, [data])

  async function fetchRates() {
    const result = await getKeywordRates(id)
    if (result) {
      setData(result)
    }
  }

  function prepareList(data = {}) {
    const { assetCount, keywordsCount, nagetiveCount, projectNagetiveCount, project: { keywords = [] } } = data
    const filter = keywords.length ? keywords : Object.keys(keywordsCount)
    const neg = keywords.length ? projectNagetiveCount : nagetiveCount
    return getKeywordList(keywordsCount, filter, neg).map(item => ({
      ...item,
      percent: percent(item.count * progressWidth / assetCount),
      total: assetCount,
      color: randomColor(),
    }))
  }

  function getKeywordList(keywords = {}, filterKeywords, negative) {
    const klist = filterKeywords.map(keyword => {
      const count = keywords[keyword] || 0
      return {
        keyword, count
      }
    })
    return [
      ...klist,
      {
        keyword: t('dataset.samples.negative'),
        count: negative,
      }
    ]
  }

  function format({ percent = 0, keyword = '', count = 0, total }) {
    return `${keyword} ${count}/${total} ${percent}`
  }

  return list.length ? (
    <div className={s.rates}>
      {list.map(item => (
        <div key={item.keyword} className={s.rate}>
          <span className={s.bar} style={{ width: item.percent, background: item.color }}>&nbsp;</span>
          <span>{format(item)}</span>
        </div>
      ))}
    </div>
  ) : null
}

const actions = (dispatch) => {
  return {
    getKeywordRates(id, force) {
      return dispatch({
        type: 'dataset/getDataset',
        payload: { id, force },
      })
    }
  }
}

export default connect(null, actions)(KeywordRates)
