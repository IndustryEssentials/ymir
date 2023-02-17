import { FC } from 'react'
import { Col, Tag } from 'antd'

import t from '@/utils/t'

import CkPopup from './CKPopup'
import ListAnnotation from '@/components/dataset/ListAnnotation'

import styles from '../assets.less'

const KeywordTagsCount = 4

const Item: FC<{ asset: YModels.Asset; showDetail: () => void; height?: number }> = ({ asset, showDetail = () => {}, height = 100 }) => (
  <Col style={{ height }} key={asset.hash} className={styles.dataset_item}>
    <CkPopup asset={asset}>
      <div className={styles.dataset_img} onClick={showDetail}>
        <ListAnnotation asset={asset} />
        <span className={styles.item_keywords_count} title={asset?.keywords.join(',')}>
          {t('dataset.detail.assets.keywords.total', {
            total: asset?.keywords?.length,
          })}
        </span>
        <span className={styles.item_keywords}>
          {asset.keywords.slice(0, 4).map((key) => (
            <Tag className={styles.item_keyword} key={key} title={key}>
              {key}
            </Tag>
          ))}
          {asset.keywords.length > KeywordTagsCount ? (
            <Tag className={styles.item_keyword} style={{ width: '10px' }}>
              ...
            </Tag>
          ) : null}
        </span>
      </div>
    </CkPopup>
  </Col>
)

export default Item
