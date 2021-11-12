import { Button, Card, Col, Descriptions, Row, Tag } from "antd"
import { useEffect, useState } from "react"
import { Link, useHistory } from "umi"
import { connect } from 'dva'

import t from '@/utils/t'
import { format } from '@/utils/date'
import EmptyState from '@/components/empty/model'
import renderTitle from './components/boxTitle'
import QuickAction from "./components/quickAction"
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { MymodelIcon, TrainIcon, } from '@/components/common/icons'

function ModelHot({ title, count = 4, batchModels, getHotModel }) {
  const history = useHistory()
  const [models, setModels] = useState([])

  useEffect(async () => {
    // setModels([
    //   {
    //     id: 1003,
    //     name: 'model name1',
    //     keywords: ['cat', 'dog', 'person', 'bottle', 'hat', 'cow', 'red hat', 'car', 'screen', 'fruit', 'pig', 'door'],
    //     map: 0.67,
    //     count: 15,
    //   },
    //   {
    //     id: 1004,
    //     name: 'model name2',
    //     keywords: ['cat', 'dog', 'person', 'bottle', 'hat'],
    //     map: 0.52,
    //     count: 12,
    //   },
    // ])
    const hots = await getHotModel(count)
    if (hots && hots.model) {
      const list = hots.model
      const ids = list.map(hot => hot[0])
      if (!ids.length) {
        return
      }
      const result = await batchModels(ids)
      if (result) {
        setModels(list.map((item, index) => ({
          count: item[1],
          ...result.find(model => model.id === item[0]),
        })))
      }
    }
  }, [])

  // const cardBodyStyle = { padding: '10px 5px', height: '160px', overflow: 'hidden' }

  return (
    <Card className={`${styles.box} ${styles.hotModel}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={renderTitle(<><MymodelIcon className={styles.headIcon} />{t('portal.model.my.title')}</>, '/home/model')}
    >
      <Row gutter={10}>
        {models.length ? (<>
          {models.map(model => <Col key={model.id} span={6}>
            <Card className={styles.boxItem} hoverable title={model.name} onClick={() => { history.push(`/home/model/detail/${model.id}`) }}>
              <Descriptions column={1} colon={false} labelStyle={{ justifyContent: 'flex-end', width: '68px' }}>
                <Descriptions.Item label={'mAP'}>{model.map}</Descriptions.Item>
                <Descriptions.Item label={t('portal.cited')}>{model.count}</Descriptions.Item>
                <Descriptions.Item label={t('portal.model.keywords')} contentStyle={{ flexWrap: 'wrap' }}>
                  <div className={styles.kwContainer}>{model?.keywords.map(keyword => <Tag className={styles.kwTag} key={keyword} title={keyword}>{keyword}</Tag>)}</div>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>)}
          <QuickAction icon={<TrainIcon style={{ fontSize: 50, color: '#36cbcb' }} />} label={t('portal.action.train')} link={'/home/task/train'}></QuickAction>
        </>) :
          <EmptyState style={{ height: 236 }} />
        }
      </Row>
    </Card>
  )
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
  }
}

export default connect(null, actions)(ModelHot)
