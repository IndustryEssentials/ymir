import { useState, useEffect } from "react"
import { Row, Col, Progress, } from "antd"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ id, total = 0, showAll = false, trainingKeywords = [], data = [], getKeywordRates }) {
  const [list, setList] = useState([])

  useEffect(() => {
    id && fetchRates()
  }, [id])

  async function fetchRates(){
    const result = await getKeywordRates(id)
    if (result) {
      const { keywords, negative_project, negative } = result
      const filter = trainingKeywords.length ? trainingKeywords : Object.keys(keywords)
      const neg = trainingKeywords.length ? negative_project : negative
      const klist = getKeywordList(keywords, filter, neg).map(item => ({
        ...item,
        width: percent(item.count * 0.8 / total, 2),
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
      keyword: 'Negative Samples',
      count: negative,
    })
    return klist
  }

  function format(percent = 0, keyword = '') {
    return `${keyword} ${percent} %`
  }

  return total ? (
    <div className={s.rates}>
      {list.map(item => (
        <div className={s.rate}>
          <span className={s.bar} style={{ width: item.width, color: item.color }}>&ngsp;</span>
          <span>{format(item.percent, item)}</span>
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
