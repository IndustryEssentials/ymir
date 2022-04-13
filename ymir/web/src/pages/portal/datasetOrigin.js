import { Button, Card, Carousel, Col, Descriptions, Row, Space, Tag } from "antd"
import { LeftOutlined, RightOutlined } from '@ant-design/icons'
import { useEffect, useState } from "react"
import { Link, useHistory } from "umi"
import { connect } from 'dva'

import styles from './index.less'
import t from '@/utils/t'
import Empty from "@/components/empty/default"
import { humanize } from '@/utils/number'
import { cardBody, cardHead } from "./components/styles"
import { FlagIcon, CopyIcon, MetadatasetIcon } from '@/components/common/icons'

function Sets({ title, count = 2, getPublicDataset }) {
  const history = useHistory()
  const [sets, setSets] = useState([])

  useEffect(async () => {
    const result = await getPublicDataset()
    if (result) {
      let r = 0, list = []
      const { items, total } = result
      while (r < total) {
        list.push(items.slice(r, r + count))
        r += count
      }
      // console.log('public dataset: ', result)
      setSets(list)
      // setSets(result.items.slice(r, r + count))
    }
  }, [])

  const boxItemTitle = (set) => (
    <>
      <Row style={{ flexWrap: 'nowrap' }}>
        <Col flex={1} title={set.name} style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{set.name}</Col>
      </Row>
      <Descriptions className={styles.setInfo} column={2}>
        <Descriptions.Item label={t('portal.dataset.asset.count')}>{humanize(set.assetCount)}</Descriptions.Item>
        <Descriptions.Item label={t('portal.dataset.keyword.count')}>
          {set?.keywords.length}
        </Descriptions.Item>
      </Descriptions>
    </>
  )

  return (
    <Card className={`${styles.box} ${styles.oset}`} bordered={false}
      headStyle={cardHead} bodyStyle={{ ...cardBody, height: 286 }}
      title={<><MetadatasetIcon className={styles.headIcon} /><span className={styles.headTitle}>{t('portal.dataset.origin.title')}</span></>}
    >
      {sets.length ?
        <Carousel arrows={true} prevArrow={<LeftOutlined />} nextArrow={<RightOutlined />}>
          {sets.map((row, index) =>
            <div key={index}>
              <Row gutter={10}>
                {row.map(set => <Col key={set.id} span={12}>
                  <Card className={styles.boxItem} title={boxItemTitle(set)}
                    style={{ position: 'relative', height: 246 }}
                    headStyle={{ padding: 0 }} bodyStyle={{ padding: '10px 0', position: 'relative', top: '-20px' }}
                  >
                    <div style={{ display: 'inline-block', marginBottom: 10, marginLeft: 10, backgroundColor: '#fff' }}>
                      <FlagIcon style={{ fontSize: 14, marginRight: 3 }} />{t('portal.dataset.keyword')}
                    </div>
                    <div className={styles.kwContainer}>
                      {set?.keywords.slice(0, 14).map(keyword => <Tag className={styles.kwTag} key={keyword} title={keyword}>{keyword}</Tag>)}
                      {set?.keywords.length > 14 ? <Tag className={styles.kwTag} title={set?.keywords.slice(11).join(',')}>...</Tag> : null}
                    </div>
                  </Card>
                </Col>)}
              </Row>
            </div>
          )}
        </Carousel> : <Empty />
      }
    </Card>
  )
}

const actions = (dispatch) => {
  return {
    getPublicDataset(ids) {
      return dispatch({
        type: "dataset/getInternalDataset",
      })
    },
  }
}

export default connect(null, actions)(Sets)
