import { Card, List, Space, Tag } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link } from "umi"

import t from '@/utils/t'
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { OptimalModelIcon } from '@/components/common/icons'
import Empty from '@/components/empty/default'

const ModelList = ({ getModels, getHotModel, batchModels }) => {
  const [models, setModels] = useState([])
  const [keywords, setKeywords] = useState([])
  const [current, setCurrent] = useState('')
  const [cacheModels, setCacheModels] = useState({})
  const [stats, setStats] = useState({})

  useEffect(async () => {
    const hots = await getHotModel(6)
    if (hots && hots.model) {
      setStats(hots.model)
      const arr = Object.keys(hots.model)
      if (!arr.length) {
        return
      }
      setKeywords(arr.slice(0, 4))
      fetchModels(arr[0], hots.model)
    }
  }, [])
  
  function changeKeyword(keyword) {
    fetchModels(keyword, stats)
  }

  async function fetchModels(keyword, stats) {
    setCurrent(keyword)
    const list = stats[keyword]
    if (cacheModels[keyword]) {
      setModels(cacheModels[keyword])
      return
    }
    const ids = list.map(hot => hot[0])
    if (!ids.length) {
      return
    }
    const result = await batchModels(ids)
    const mls = result && result.length ?
      result.map((item, index) => ({
        count: list.find(i => i[0] === item.id)[1],
        ...item,
      })) : []
    setModels(mls)
    if (!cacheModels[keyword]) {
      setCacheModels({
        ...cacheModels,
        [keyword]: mls,
      })
    }
  }

  return <Card className={`${styles.box} ${styles.modelList}`}
    headStyle={cardHead} bodyStyle={{ ...cardBody, height: 281 }}
    title={<><OptimalModelIcon className={styles.headIcon} />{t('portal.model.best.title')}</>}
  >
    <Space>{keywords.map(k => <Tag className={`${k === current ? styles.current : ''} ${styles.kwtag}`} key={k} onClick={() => changeKeyword(k)}>{k}</Tag>)}</Space>
    <List className={styles.boxItem} bordered={false}>
      {models.length ? models.map((model, index) =>
        <List.Item key={model.id} actions={[<span className={styles.action}>{model.map}</span>]} title={model.name}>
          <Link className={styles.modelListItem} to={`/home/model/detail/${model.id}`}>
            <span className={`${styles['ol' + index]} ${styles.ol}`}>{index + 1}</span>
            {model.name}
          </Link>
        </List.Item>
      ) : <Empty />
      }
    </List>
  </Card>
}

const actions = (dispatch) => {
  return {
    getHotModel(limit) {
      return dispatch({
        type: "common/getStats",
        payload: { q: 'model', limit },
      })
    },
    batchModels(ids) {
      return dispatch({
        type: "model/batchModels",
        payload: ids,
      })
    },
    getModels() {
      return dispatch({
        type: 'model/getModels',
        payload: { offset: 0, limit: 7, sort_by_map: true, },
      })
    }
  }
}

export default connect(null, actions)(ModelList)
