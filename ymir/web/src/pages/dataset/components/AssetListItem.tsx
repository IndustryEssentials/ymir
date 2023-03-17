import { FC, useCallback, useEffect, useState } from 'react'
import { Col, Tag } from 'antd'

import t from '@/utils/t'

import CkPopup from './CKPopup'
import ListAnnotation from '@/components/dataset/ListAnnotation'

import styles from '../assets.less'
import VisualModes from './VisualModes'

const KeywordTagsCount = 4

const Item: FC<{ asset: YModels.Asset; showDetail: () => void; height?: number; mode?: VisualModes }> = ({
  asset,
  showDetail = () => {},
  height = 100,
  mode = 0,
}) => {
  const [visibles, setVisibles] = useState<{ [key: string]: boolean }>({
    asset: true,
    gt: true,
    pred: true,
  })

  useEffect(() => {
    let visibleItems: string[] = []
    switch (mode) {
      case VisualModes.All:
        visibleItems = ['asset', 'gt', 'pred']
        break
      case VisualModes.Asset:
        visibleItems = ['asset']
        break
      case VisualModes.Gt:
        visibleItems = ['asset', 'gt']
        break
      case VisualModes.Pred:
        visibleItems = ['asset', 'pred']
        break
      case VisualModes.GtPred:
        visibleItems = ['gt', 'pred']
        break
    }
    setVisibles(
      visibleItems.reduce(
        (prev, curr) => ({
          ...prev,
          [curr]: true,
        }),
        {},
      ),
    )
  }, [mode])

  const filterAnnotations = useCallback(
    (annotations: YModels.Annotation[]) => annotations.filter((annotation) => (visibles['gt'] && annotation.gt) || (visibles['pred'] && !annotation.gt)),
    [visibles],
  )

  return (
    <Col style={{ height }} key={asset.hash} className={styles.dataset_item}>
      <CkPopup asset={asset}>
        <div className={styles.dataset_img} onClick={showDetail}>
          <ListAnnotation asset={asset} hideAsset={!visibles['asset']} filter={filterAnnotations} isFull={true} />
          {mode === VisualModes.Asset ? null : (
            <>
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
            </>
          )}
        </div>
      </CkPopup>
    </Col>
  )
}

export default Item
