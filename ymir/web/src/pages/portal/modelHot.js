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

function ModelHot({ getModels }) {
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
    const result = await getModels(order)
    if (result) {
      setModels(result.items)
    }
  }

  // const cardBodyStyle = { padding: '10px 5px', height: '160px', overflow: 'hidden' }

  return (
    <Card className={`${styles.box} ${styles.hotModel}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={<Title title={<><MymodelIcon className={styles.headIcon} />{t('portal.model.my.title')}</>} link='/home/model'>
        <Radio.Group style={{ marginRight: 40 }} optionType='button' defaultValue={options[0].value} options={options} onChange={changeOrder} />
      </Title>}
    >
      <Row gutter={10}>
        {models.length ? (<>
          {models.map(model => <Col key={model.id} span={6}>
            <Card className={styles.boxItem} hoverable title={model.name} onClick={() => { history.push(`/home/model/detail/${model.id}`) }}>
              <Descriptions column={1} colon={false} labelStyle={{ justifyContent: 'flex-end', width: '68px' }}>
                <Descriptions.Item label={'mAP'}>{model.map}</Descriptions.Item>
                {/* <Descriptions.Item label={t('portal.cited')}>{model.count}</Descriptions.Item> */}
                <Descriptions.Item label={t('portal.model.keywords')} contentStyle={{ flexWrap: 'wrap' }}>
                  <div className={styles.kwContainer}>{model?.keywords.map(keyword => <Tag className={styles.kwTag} key={keyword} title={keyword}>{keyword}</Tag>)}</div>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </Col>)}
          <QuickAction icon={<TrainIcon style={{ fontSize: 50, color: '#36cbcb' }} />} label={t('portal.action.train')} link={'/home/task/train'}></QuickAction>
        </>) :
          <EmptyState style={{ height: 230 }} />
        }
      </Row>
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getModels(order_by) {
      return dispatch({
        type: 'model/getModels',
        payload: { offset: 0, limit: 3, order_by, },
      })
    },
  }
}

export default connect(null, actions)(ModelHot)
