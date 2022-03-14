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
  const [list, setList] = useState([])

  useEffect(() => {
    id && fetchRates()
  }, [id])

  async function fetchRates(){
    const result = await getKeywordRates(id)
    if (result) {
      const { total, keywords, negative_project, negative } = result
      const filter = trainingKeywords.length ? trainingKeywords : Object.keys(keywords)
      const neg = trainingKeywords.length ? negative_project : negative
      const klist = getKeywordList(keywords, filter, neg).map(item => ({
        ...item,
        percent: percent(item.count * 0.8 / total),
        total,
        color: randomColor(),
      }))
      setList(klist)
    }
  }

  function getKeywordList(keywords, filterKeywords, negative ) {
    const klist = filterKeywords.map(keyword => {
      const count = keywords[keyword]
      return {
        keyword, count
      }
    })
    klist.push({
      keyword: t('dataset.samples.negative'),
      count: negative,
    })
    return klist
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
