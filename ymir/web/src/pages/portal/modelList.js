import { Card, List, Space, Tag } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link } from "umi"

import t from '@/utils/t'
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { OptimalModelIcon } from '@/components/common/icons'
import Empty from '@/components/empty/default'

const ModelList = ({ getModelsByMap }) => {
  const [models, setModels] = useState([])
  const [keywords, setKeywords] = useState([])
  const [current, setCurrent] = useState('')

  useEffect(() => {
      fetchModels()
  }, [])
  
  function changeKeyword(keyword) {
    setCurrent(keyword)
  }

  async function fetchModels() {
    const { models, keywords } = await getModelsByMap(35)
    setModels(models)
    setKeywords(keywords)

    setCurrent(keywords[0])
  }

  return <Card className={`${styles.box} ${styles.modelList}`}
    headStyle={cardHead} bodyStyle={{ ...cardBody, height: 281 }}
    title={<><OptimalModelIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.model.best.title')}</span></>}
  >
    <Space>{keywords.map(k => <Tag className={`${k === current ? styles.current : ''} ${styles.kwtag}`} key={k} onClick={() => changeKeyword(k)}>{k}</Tag>)}</Space>
    <List className={styles.boxItem} bordered={false}>
      {models.length ? models.filter((model, index) => model.keywords.indexOf(current) >= 0 && index < 7).map((model, index) =>
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
    getModelsByMap(limit = 5) {
      return dispatch({
        type: 'model/getModelsByMap',
        payload: { limit },
      })
    },
  }
}

export default connect(null, actions)(ModelList)
