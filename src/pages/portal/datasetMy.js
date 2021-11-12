import { Badge, Button, Card, Col, Descriptions, Row, Tag, Statistic } from "antd"
import { useEffect, useState } from "react"
import { Link, useHistory } from "umi"
import { connect } from 'dva'

import t from '@/utils/t'
import { humanize } from "@/utils/number"
import EmptyState from '@/components/empty/dataset'
import renderTitle from "./components/boxTitle"
import QuickAction from "./components/quickAction"
import { MydatasetIcon, ImportIcon } from '@/components/common/icons'
import { cardHead, cardBody } from "./components/styles"
import styles from './index.less'

function Sets({ title, count = 3, batchDatasets, getHotDataset }) {
  const history = useHistory()
  const [sets, setSets] = useState([])

  useEffect(async () => {
    // setSets([
    //   {
    //     id: 1003,
    //     name: 'dataset name1',
    //     keywords: ['cat', 'dog', 'person', 'bottle', 'hat', 'cow', 'red hat', 'car', 'screen', 'fruit', 'pig', 'door'],
    //     asset_count: 3000224343,
    //     count: 15,
    //     create_time: '11/14',
    //   },
    //   {
    //     id: 1004,
    //     name: 'dataset name2',
    //     keywords: ['cat', 'dog', 'person', 'bottle', 'hat'],
    //     asset_count: 459,
    //     count: 12,
    //   },
    //   {
    //     id: 1005,
    //     name: 'dataset name3',
    //     keywords: ['cat', 'dog', 'person', 'hello'],
    //     asset_count: 7658,
    //     count: 11,
    //   },
    //   // {
    //   //   id: 1006,
    //   //   name: 'dataset name4',
    //   //   keywords: ['cat', 'dog', 'person'],
    //   //   asset_count: 300000,
    //   //   count: 11,
    //   // },
    // ])
    // return
    const hots = await getHotDataset(count)
    if (hots && hots.dataset) {
      const list = hots.dataset
      const ids = list.map(hot => hot[0])
      if (!ids.length) {
        return
      }
      const result = await batchDatasets(ids.slice(0, count))
      if (result) {
        const sets = list.map((item, index) => {
          const ds = result.find(dataset => dataset.id === item[0])
          if (ds) {
            return {
              count: item[1],
              ...ds,
            }
          }
        })
        setSets(sets.filter(s => s))
      }
    }
  }, [])

  const BoxTitle = ({ set }) => (
    <>
      <h4 className={styles.boxItemTitle}>{set.name}</h4>
      <Row>
        <Col span={8} title={set.asset_count}>
          <Statistic className={styles.boxItemTitleCount} title={t("portal.dataset.asset.count")} value={humanize(set.asset_count)} />
        </Col>
        <Col span={8} title={set.keywords.length}>
          <Statistic className={styles.boxItemTitleCount} title={t("portal.dataset.keyword.count")} value={humanize(set.keywords.length)} />
        </Col>
        <Col span={8} title={set.count}>
          <Statistic className={styles.boxItemTitleCount} title={t("portal.cited")} value={humanize(set.count)} />
        </Col>
      </Row>
    </>
  )

  return (
    <Card className={styles.box} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={renderTitle(<><MydatasetIcon className={styles.headIcon} />{t('portal.dataset.my.title')}</>, '/home/dataset')}
    >
      <Row gutter={10} wrap='nowrap'>
        {sets.length ? <>
          {sets.map(set => <Col key={set.id} lg={8} xl={6}>
            <Card
              className={styles.boxItem}
              hoverable
              title={<BoxTitle set={set} />}
              onClick={() => { history.push(`/home/dataset/detail/${set.id}`) }}
            >
              {set?.keywords.length ? 
              <Descriptions column={1}>
                <Descriptions.Item label={t('portal.dataset.keyword')}>
                  <div className={styles.kwContainer}>
                    {set?.keywords.slice(0, 11).map(keyword => <Tag className={styles.kwTag} key={keyword} title={keyword}>{keyword}</Tag>)}
                    {set?.keywords.length > 11 ? <Tag className={styles.kwTag} title={set?.keywords.slice(11).join('\n')}>...</Tag> : null}
                  </div>
                </Descriptions.Item>
              </Descriptions> : null }
            </Card>
          </Col>)}
          <QuickAction 
            icon={<ImportIcon style={{ fontSize: 50, color: '#36cbcb' }} />} 
            label={t('portal.action.dataset.import')} 
            link={{ pathname: '/home/dataset', state: { type: 'add' }}}
          />
        </>
          : <EmptyState style={{ height: 236 }} add={() => history.push({ pathname: '/home/dataset', state: { type: 'add' }})} />}
      </Row>
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getHotDataset(limit) {
      return dispatch({
        type: "common/getStats",
        payload: { q: 'dataset', limit },
      })
    },
    batchDatasets(ids) {
      return dispatch({
        type: "dataset/batchDatasets",
        payload: ids,
      })
    },
  }
}

export default connect(null, actions)(Sets)
