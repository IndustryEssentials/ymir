import { useState, useEffect } from "react"
import { Row, Col, Progress, } from "antd"
import t from "@/utils/t"

import s from "./keywordRates.less"
import { toFixed } from "@/utils/number"

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
        percent: Number(toFixed(item.count / total, 4)) * 100,
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

  function format(percent, item) {
    return `${item.keyword} ${percent} %`
  }

  return total ? (
    <div className={s.keywordRates}>
      {list.map(item => (
        <Row>
          <Col>width</Col>
          <Col flex={'20%'}>{format(item.percent, item)}</Col>
          </Row>
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
