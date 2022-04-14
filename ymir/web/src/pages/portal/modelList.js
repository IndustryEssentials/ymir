import { Card, List, Space, Tag } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link } from "umi"

import t from '@/utils/t'
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { OptimalModelIcon } from '@/components/common/icons'
import Empty from '@/components/empty/default'
import { percent } from "../../utils/number"

const ModelList = ({ getModelsByMap }) => {
  const [keywords, setKeywords] = useState([])
  const [current, setCurrent] = useState('')
  const [kmodels, setKModels] = useState({})

  useEffect(() => {
      fetchModels()
  }, [])
  
  function changeKeyword(keyword) {
    setCurrent(keyword)
  }

  async function fetchModels() {
    const { keywords, kmodels } = await getModelsByMap(35)
    setKeywords(keywords)
    setKModels(kmodels)
    setCurrent(keywords[0])
  }

  return <Card className={`${styles.box} ${styles.modelList}`}
    headStyle={cardHead} bodyStyle={{ ...cardBody, height: 286 }}
    title={<><OptimalModelIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.model.best.title')}</span></>}
  >
    <div><span>{t('common.index.keyword.label')}: </span>{keywords.map(k => <Tag className={`${k === current ? styles.current : ''} ${styles.kwtag}`} key={k} onClick={() => changeKeyword(k)}>{k}</Tag>)}</div>
    <List className={styles.boxItem} bordered={false}>
      {kmodels[current]?.length ? kmodels[current]?.filter(model => model).map((model, index) =>
        <List.Item key={model.id} actions={[<span className={styles.action} title={model.map}>{percent(model.map)}</span>]} title={model.name}>
          <Link className={styles.modelListItem} to={`/home/project/${model.projectId}/model/${model.id}`}>
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
