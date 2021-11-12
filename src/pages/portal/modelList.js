import { Card, List } from "antd"
import { useEffect, useState } from "react"
import { connect } from 'dva'
import { Link } from "umi"

import t from '@/utils/t'
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { OptimalModelIcon } from '@/components/common/icons'
import Empty from '@/components/empty/default'

const ModelList = ({ getModels }) => {
  const [models, setModels] = useState([])

  useEffect(async () => {
    const result = await getModels()
    if (result) {
      setModels(result.items)
    }
  }, [])

  return <Card className={`${styles.box} ${styles.modelList}`}
    headStyle={cardHead} bodyStyle={cardBody}
    title={<><OptimalModelIcon className={styles.headIcon} />{t('portal.model.best.title')}</>}
  >
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
    getModels() {
      return dispatch({
        type: 'model/getModels',
        payload: { offset: 0, limit: 7, sort_by_map: true, },
      })
    }
  }
}

export default connect(null, actions)(ModelList)
