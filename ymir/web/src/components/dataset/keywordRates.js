import { useState, useEffect } from "react"
import { Row, Col, Progress, } from "antd"
import { connect } from 'dva'
import t from "@/utils/t"

import s from "./keywordRates.less"
import { percent } from "@/utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ dataset, progressWidth = 0.5, getKeywordRates }) {
  const [data, setData] = useState({})
  const [list, setList] = useState([])

  useEffect(() => {
    if(dataset?.id) {
      setData(dataset)
    } else if(dataset) {
      fetchRates(dataset)
    } else {
      setData({})
      setList([])
    }
  }, [dataset])

  useEffect(() => {
    if (data) {
      const klist = prepareList(data)
      setList(klist)
    }
  }, [data])

  async function fetchRates(id) {
    const result = await getKeywordRates(id)
    if (result) {
      setData(result)
    }
  }

  function prepareList(dataset = {}) {
    if (!dataset?.id) {
      return []
    }
    const { assetCount, keywordsCount, nagetiveCount, projectNagetiveCount, project: { keywords = [] } } = dataset
    const filter = keywords.length ? keywords : Object.keys(keywordsCount)
    const neg = keywords.length ? projectNagetiveCount : nagetiveCount
    const kwList = getKeywordList(keywordsCount, filter, neg)
    const widthRate = assetCount / Math.max(...(kwList.map(item => item.count)))
    const getWidth = (count) => percent(count * progressWidth * widthRate / assetCount)
    return kwList.map(item => ({
      ...item,
      width: getWidth(item.count),
      percent: percent(item.count / assetCount),
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
          <span className={s.bar} style={{ width: item.width, background: item.color }}>&nbsp;</span>
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
