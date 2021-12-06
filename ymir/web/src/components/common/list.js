import React, { useEffect, useState } from "react"
import styles from "./list.less"
import { List, Button } from "antd"

const MoreList = ({
  getData,
  offset = 0,
  limit = 10,
  field = "id",
  header,
  actions,
}) => {
  const [initLoading, setInitLoading] = useState(true)
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState([])
  const [data, setData] = useState([])
  const [pageStart, setPageStart] = useState(0)
  const [end, setEnd] = useState(false)

  useEffect(async () => {
    setLoading(true)
    let res = await getData({ limit, offset: pageStart })
    if (res.data && res.data.items) {
      const tempData = [...data, ...res.data.items]
      setData(tempData)
      setList(tempData)
      setEnd(true)
    }
    setInitLoading(false)
    setLoading(false)
    window.dispatchEvent(new Event("resize"))
  }, [pageStart, limit])

  const loadMore = () => {
    setList(
      list.concat(
        [...new Array(limit)].map(() => ({ loading: true, name: {} }))
      )
    )
    setPageStart((pageStart) => pageStart + limit)
  }

  const moreBtn =
    !initLoading && !end && !loading ? (
      <div className={styles.more}>
        <Button onClick={loadMore}>More...</Button>
      </div>
    ) : null

  const renderItem = (item) => {
    const getActions = actions(item)
    return <List.Item actions={getActions}>{item[field]}</List.Item>
  }

  return (
    <List
      className={styles.list}
      loading={initLoading}
      header={header}
      itemLayout="horizontal"
      loadMore={moreBtn}
      dataSource={list}
      renderItem={renderItem}
    />
  )
}

export default MoreList
