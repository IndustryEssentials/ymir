import { useState, useEffect } from "react"
import { Row, Col, Progress, } from "antd"
import { connect } from 'dva'
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ id, trainingKeywords = [], getKeywordRates }) {
  const [data, setData] = useState(null)
  const [list, setList] = useState([])

  useEffect(() => {
    id && fetchRates()
  }, [id])

  useEffect(() => {
    if (data) {
      const klist = prepareList(data, trainingKeywords)
      console.log(klist, trainingKeywords, 'params')
      setList(klist)
    }
  }, [data, trainingKeywords])

  async function fetchRates() {
    const result = await getKeywordRates(id)
    if (result) {
      setData(result)
    }
  }

  function prepareList(data = {}, trainingKeywords = []) {
    const { keywordCount, keywordsCount, nagetiveCount, projectNagetiveCount } = data
    const filter = trainingKeywords.length ? trainingKeywords : Object.keys(keywordsCount)
    const neg = trainingKeywords.length ? projectNagetiveCount : nagetiveCount
    return getKeywordList(keywords, filter, neg).map(item => ({
      ...item,
      percent: percent(item.count * 0.8 / total),
      total: keywordCount,
      color: randomColor(),
    }))
  }

  function getKeywordList(keywords, filterKeywords, negative) {
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
    getKeywordRates(id) {
      return dispatch({
        type: 'dataset/getKeywordRates',
        payload: id,
      })
    }
  }
}

export default connect(null, actions)(KeywordRates)
