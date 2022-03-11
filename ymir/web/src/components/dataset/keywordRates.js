import { useState, useEffect } from "react"
import { Row, Col, } from "antd"
import t from "@/utils/t"

import style from "./tripleRates.less"
import { percent } from "../../utils/number"

function randomColor() {
  return "#" + Math.random().toString(16).slice(-6)
}

function KeywordRates({ total = 0, showAll = false, trainingKeywords = [], data = [] }) {
  const [list, setList] = useState([])
  useEffect(() => {
    if (data.length) {
      const klist = data.map(({ label, count = 0}) => {
        return {

        }
      })
    }
  }, [data])
  useEffect(() => {
    setTotal(0)
    const sums = parts.map((part, index) => {
      const sum = data.reduce((prev, curr) => part.ids.indexOf(curr.id) >= 0 ? prev + curr.asset_count : prev, 0)
      setTotal(total => total + sum)
      return {
        ...part,
        color: colors[index],
        sum,
      }
    })
    setCounts(sums)

  }, [parts])

  function format(num) {
    return percent(num / total)
  }

  return total ? (
    <Row className={style.container} gutter={20}>
      <Col className={style.progress} flex={1}>
        <Row className={style.bg} wrap={false}>
          {counts.map((part, index) => part.sum > 0 ? (
            <Col className={style.part} flex={format(part.sum)} key={index} style={{ backgroundColor: part.color }} title={format(part.sum)}>
              {part.label} {format(part.sum)}
            </Col>
          ) : null)}
        </Row>
      </Col>
      <Col>{t('task.train.total.label', { total })}</Col>
    </Row>
  ) : null
}

export default KeywordRates
