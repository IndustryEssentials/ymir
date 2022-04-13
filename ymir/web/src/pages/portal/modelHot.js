import { Button, Card, Col, Descriptions, Row, Space, Tag, Radio } from "antd"
import { useEffect, useState } from "react"
import { Link, useHistory } from "umi"
import { connect } from 'dva'

import t from '@/utils/t'
import EmptyState from '@/components/empty/model'
import Title from './components/boxTitle'
import QuickAction from "./components/quickAction"
import styles from './index.less'
import { cardBody, cardHead } from "./components/styles"
import { MymodelIcon, TrainIcon, } from '@/components/common/icons'
import { options, ORDER } from "./components/orderOptions"
import { percent } from "../../utils/number"

function ModelHot({ getLatestModels, getHotModels }) {
  const history = useHistory()
  const [models, setModels] = useState([])

  useEffect(async () => {
    fetchModels(ORDER.hot)
  }, [])

  function changeOrder({ target }) {
    const order = target.value ? target.value : undefined
    fetchModels(order)
  }

  async function fetchModels(order) {
    let result = null
    if (order === ORDER.hot) {
      result = await getHotModels()
    } else {
      const modelsObj = await getLatestModels()
      result = modelsObj.items
    }
    if (result) {
      setModels(result)
    }
  }

  return (
    <Card className={`${styles.box} ${styles.hotModel}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={<Title title={<><MymodelIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.model.my.title')}</span></>} link='/home/model'>
        <Radio.Group className={styles.tabLatestHot} optionType='button' defaultValue={options[0].value} options={options} onChange={changeOrder} />
      </Title>}
    >
      <Row gutter={10}>
        {models.length ? (<>
          {models.map(model => <Col key={model.id} span={6}>
            <Card className={styles.boxItem} hoverable title={model.name} onClick={() => { history.push(`/home/project/${model.projectId}/model/${model.id}`) }}>
              <Descriptions column={1} colon={false} labelStyle={{ justifyContent: 'flex-end', width: '68px' }}>
                <Descriptions.Item className={styles.mapValue} label={'mAP'}><span title={model.map}>{percent(model.map)}</span></Descriptions.Item>
                { model.count ? <Descriptions.Item label={t('portal.cited')}>{model.count}</Descriptions.Item> : null }
                <Descriptions.Item label={t('portal.model.keywords')} contentStyle={{ flexWrap: 'wrap' }}>
                  <div className={styles.kwContainer}>{model?.keywords.map(keyword => <Tag className={styles.kwTag} key={keyword} title={keyword}>{keyword}</Tag>)}</div>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>)}
          <QuickAction icon={<TrainIcon style={{ fontSize: 50, color: '#36cbcb' }} />} label={t('portal.action.train')} link={'/home/task/train'}></QuickAction>
        </>) :
          <EmptyState style={{ height: 246 }} />
        }
      </Row>
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getLatestModels(limit = 3) {
      return dispatch({
        type: 'model/getModels',
        payload: { offset: 0, limit, },
      })
    },
    getHotModels(limit = 3) {
      return dispatch({
        type: 'model/getModelsByRef',
        payload: { limit }
      })
    },
  }
}

export default connect(null, actions)(ModelHot)
