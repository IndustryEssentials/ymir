import { Badge, Button, Card, Col, Descriptions, Row, Tag, Statistic, Radio } from "antd"
import { useEffect, useState } from "react"
import { Link, useHistory } from "umi"
import { connect } from 'dva'

import t from '@/utils/t'
import { humanize } from "@/utils/number"
import EmptyState from '@/components/empty/dataset'
import Title from "./components/boxTitle"
import QuickAction from "./components/quickAction"
import { MydatasetIcon, ImportIcon } from '@/components/common/icons'
import { cardHead, cardBody } from "./components/styles"
import styles from './index.less'
import { options, ORDER } from "./components/orderOptions"

function Sets({ count = 3, getHotDataset, getDatasets }) {
  const history = useHistory()
  const [sets, setSets] = useState([])

  useEffect(async () => {
    fetchHotDataset()
  }, [])

  function changeOrder({ target }) {
    if (target.value === ORDER.hot) {
      fetchHotDataset()
    } else {
      fetchLatestDataset()
    }
  }

  async function fetchHotDataset() {
    const result = await getHotDataset(count)
    if (result) {
      setSets(sets.filter(s => s))
    }
  }

  async function fetchLatestDataset() {
    const result = await getDatasets()
    if (result) {
      setSets(result.items)
    }
  }

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
          {set.count !== undefined ? <Statistic className={styles.boxItemTitleCount} title={t("portal.cited")} value={humanize(set.count)} /> : null}
        </Col>
      </Row>
    </>
  )

  return (
    <Card id='mydataset' className={`${styles.box} ${styles.myDataset}`} bordered={false}
      headStyle={cardHead} bodyStyle={cardBody}
      title={<Title title={<><MydatasetIcon className={styles.headIcon} />{t('portal.dataset.my.title')}</>} link='/home/dataset'>
        <Radio.Group style={{ marginRight: 40 }} optionType='button' defaultValue={options[0].value} options={options} onChange={changeOrder} />
      </Title>}
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
                </Descriptions> : null}
            </Card>
          </Col>)}
          <QuickAction
            icon={<ImportIcon style={{ fontSize: 50, color: '#36cbcb' }} />}
            label={t('portal.action.dataset.import')}
            link={'/home/dataset/add'}
          />
        </>
          : <EmptyState style={{ height: 230 }} add={() => history.push('/home/dataset/add')} />}
      </Row>
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getHotDatasets(limit = 3) {
      return dispatch({
        type: "dataset/getHotDatasets",
        payload: { limit },
      })
    },
    getDatasets(limit = 3) {
      return dispatch({
        type: "dataset/getDatasets",
        payload: { limit, state: 3 },
      })
    },
  }
}

export default connect(null, actions)(Sets)
