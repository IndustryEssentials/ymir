import { FC, useEffect, useState } from 'react'
import { Col, Row, Tag } from 'antd'

import t from '@/utils/t'

import CkPopup from './CKPopup'
import ListAnnotation from '@/components/dataset/ListAnnotation'
import DefaultEmpty from '@/components/empty/default'

import styles from '../assets.less'

type Props = {
  list?: YModels.Asset[]
  goAsset?: (asset: YModels.Asset, hash: string, current: number) => void
  width?: number
  columns?: number
}

const KeywordTagsCount = 4
const ItemSpace = 4

const List: FC<Props> = ({ list = [], goAsset = () => {}, width = 0, columns = 5 }) => {
  const [rows, setRows] = useState<YModels.Asset[][]>([])

  useEffect(() => {
    let r = 0
    let result: YModels.Asset[][] = []
    while (r < list.length) {
      result.push(list.slice(r, r + columns))
      r += columns
    }
    setRows(result)
  }, [list])

  return rows.length ? (
    <>
      {rows.map((row, index) => {
        const h =
          (width - ItemSpace * columns) /
          row.reduce((prev, asset) => {
            const { width = 0, height = 0 } = asset?.metadata || {}
            return height ? prev + width / height : prev
          }, 0)

        return (
          <Row gutter={ItemSpace} wrap={false} key={index} className={styles.dataset_container}>
            {row.map((asset, rowIndex) => (
              <Col style={{ height: h }} key={asset.hash} className={styles.dataset_item}>
                <CkPopup asset={asset}>
                  <div className={styles.dataset_img} onClick={() => goAsset(asset, asset.hash, index * columns + rowIndex)}>
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
            ))}
          </Row>
        )
      })}
    </>
  ) : (
    <DefaultEmpty />
  )
}

export default List
