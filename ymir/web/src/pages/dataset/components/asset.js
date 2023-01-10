import React, { useEffect, useState } from 'react'
import { Button, Card, Col, Descriptions, Row, Tag, Space } from 'antd'

import { getDateFromTimestamp } from '@/utils/date'
import t from '@/utils/t'
import { randomBetween } from '@/utils/number'
import useFetch from '@/hooks/useFetch'
import useRequest from '@/hooks/useRequest'

import Hash from '@/components/common/hash'
import AssetAnnotation from '@/components/dataset/asset/AssetAnnotations'
import GtSelector from '@/components/form/GtSelector'
import EvaluationSelector from '@/components/form/EvaluationSelector'
import CustomLabels from '@/components/dataset/asset/CustomLabels'

import styles from './asset.less'
import { NavDatasetIcon, EyeOffIcon, EyeOnIcon } from '@/components/common/Icons'
import { LeftOutlined, RightOutlined } from '@ant-design/icons'

const { CheckableTag } = Tag
const { Item } = Descriptions

function Asset({ id, asset: cache, datasetKeywords, filterKeyword, filters, index = 0, total = 0 }) {
  const [asset, setAsset] = useState({})
  const [current, setCurrent] = useState('')
  const [showAnnotations, setShowAnnotations] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [currentIndex, setCurrentIndex] = useState(null)
  const [assetHistory, setAssetHistory] = useState([])
  const [evaluation, setEvaluation] = useState({ selected: [], all: false })
  const [gtSelected, setGtSelected] = useState({ selected: [], all: false })
  const [colors, setColors] = useState({})
  const [{ items: assets }, getAssets] = useFetch('dataset/getAssetsOfDataset', { items: [] })
  const { data: dataset, run: getDataset } = useRequest('dataset/getDataset', {
    loading: false,
  })

  useEffect(() => {
    getDataset({ id })
  }, [])

  useEffect(() => {
    setAsset({})
    index > -1 && setCurrentIndex({ index, keyword: filterKeyword })
  }, [index, filterKeyword])

  useEffect(() => {
    if (currentIndex !== null) {
      fetchAssetHash()
      setAssetHistory((history) => [...history, currentIndex])
    }
  }, [currentIndex])

  useEffect(() => {
    if (cache) {
      setAsset(cache)
      setCurrent(cache.hash)
    }
  }, [cache])

  useEffect(() => {
    if (!asset.hash) {
      return
    }
    const { annotations } = asset
    setSelectedKeywords(asset.keywords)
    setCurrent(asset.hash)
    setColors(annotations.reduce((prev, annotation) => ({ ...prev, [annotation.keyword]: annotation.color }), {}))
  }, [asset])

  useEffect(() => {
    assets.length && setAsset(assets[0])
  }, [assets])

  useEffect(() => {
    const keywordFilter = (annotation) => selectedKeywords.indexOf(annotation.keyword) >= 0
    const typeAll = !gtSelected.selected.length || gtSelected.all
    const cmAll = !evaluation.selected.length || evaluation.all
    const gtFilter = (annotation) => typeAll || gtSelected.selected.some((selected) => (selected === 'gt' ? annotation.gt : !annotation.gt))
    const evaluationFilter = (annotation) => cmAll || evaluation.selected.includes(annotation.cm)
    const filters = (annotation) => keywordFilter(annotation) && evaluationFilter(annotation) && gtFilter(annotation)
    const visibleAnnotations = (asset.annotations || []).filter(filters)
    setShowAnnotations(visibleAnnotations)
  }, [selectedKeywords, evaluation, asset, gtSelected])

  function fetchAssetHash() {
    setAsset((asset) => ({ ...asset, annotations: [] }))
    getAssets({ id, ...filters, keyword: currentIndex.keyword, offset: currentIndex.index, limit: 1, datasetKeywords })
  }

  function next() {
    setCurrentIndex((cu) => ({ ...cu, index: cu.index + 1 }))
  }

  function prev() {
    setCurrentIndex((cu) => ({ ...cu, index: cu.index - 1 }))
  }

  function random() {
    setCurrentIndex((cu) => ({ ...cu, index: randomBetween(0, total - 1, cu.index) }))
  }

  function back() {
    const item = assetHistory[assetHistory.length - 2]
    if (typeof item !== 'undefined') {
      const hist = assetHistory.slice(0, assetHistory.length - 2)
      setAssetHistory(hist)
      setCurrentIndex(item)
    }
  }

  function changeKeywords(tag, checked) {
    const selected = checked ? [...selectedKeywords, tag] : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  function toggleAnnotation() {
    setSelectedKeywords(selectedKeywords.length ? [] : asset.keywords)
  }

  function gtChange(checked, all) {
    setGtSelected({ selected: checked, all })
  }

  function evaluationChange(checked, all) {
    setEvaluation({ selected: checked, all })
  }

  return asset.hash ? (
    <div className={styles.asset}>
      <div className={styles.info}>
        <Row className={styles.infoRow} align="center" wrap={false}>
          <Col flex={'20px'} style={{ alignSelf: 'center' }}>
            <LeftOutlined hidden={currentIndex.index <= 0} className={styles.prev} onClick={prev} />
          </Col>
          <Col flex={1} className={`${styles.asset_img} scrollbar`}>
            {asset.annotations ? <AssetAnnotation asset={{ ...asset, annotations: showAnnotations }} /> : null}
          </Col>
          <Col span={6} className={styles.asset_info}>
            <Card
              title={
                <>
                  <NavDatasetIcon /> {t('dataset.asset.info')}
                </>
              }
              bordered={false}
              className="noShadow"
              style={{ marginRight: 20 }}
              headStyle={{ paddingLeft: 0 }}
              bodyStyle={{ padding: '20px 0' }}
            >
              <Descriptions
                bordered
                column={2}
                contentStyle={{ flexWrap: 'wrap', padding: '10px' }}
                labelStyle={{ justifyContent: 'flex-end', padding: '10px' }}
              >
                <Item label={t('dataset.asset.info.id')} span={2}>
                  <Hash value={current} />
                </Item>
                <Item label={t('dataset.asset.info.width')}>{asset.metadata?.width}</Item>
                <Item label={t('dataset.asset.info.height')}>{asset.metadata?.height}</Item>
                {asset.size ? <Item label={t('dataset.asset.info.size')}>{asset.size}</Item> : null}
                <Item label={t('dataset.asset.info.channel')} span={asset.size ? 1 : 2}>
                  {asset.metadata?.image_channels}
                </Item>
                <Item label={t('dataset.asset.info.timestamp')} span={2}>
                  {getDateFromTimestamp(asset.metadata?.timestamp?.start)}
                </Item>
                <Item label={t('dataset.asset.info.keyword')} span={2}>
                  <Row>
                    <Col flex={1}>
                      {asset.keywords?.map((keyword, i) => (
                        <CheckableTag
                          checked={selectedKeywords.indexOf(keyword) > -1}
                          onChange={(checked) => changeKeywords(keyword, checked)}
                          className={'ant-tag-' + colors[keyword]}
                          key={i}
                          color={colors[keyword]}
                        >
                          {keyword}
                        </CheckableTag>
                      ))}
                    </Col>
                    <Col>
                      {selectedKeywords.length ? (
                        <EyeOnIcon onClick={toggleAnnotation} title={t('dataset.asset.annotation.hide')} />
                      ) : (
                        <EyeOffIcon onClick={toggleAnnotation} title={t('dataset.asset.annotation.show')} />
                      )}
                    </Col>
                  </Row>
                </Item>
                <Item label={t('dataset.assets.keyword.selector.types.cks')}>
                  <CustomLabels asset={asset} />
                </Item>
              </Descriptions>

              <Space className={styles.filter} size={10} wrap>
                <GtSelector vertical onChange={gtChange} />
                <EvaluationSelector hidden={!dataset?.evaluated || !asset.evaluated} vertical onChange={evaluationChange} />
              </Space>
            </Card>
            <Space className={styles.random}>
              <Button type="primary" style={{ marginTop: 20 }} onClick={random}>
                {t('dataset.asset.random')}
              </Button>
              <Button className={styles.back} type="primary" style={{ marginTop: 20 }} onClick={back}>
                {t('dataset.asset.back')}
              </Button>
            </Space>
          </Col>
          <Col style={{ alignSelf: 'center' }} flex={'20px'}>
            <RightOutlined hidden={currentIndex.index >= total - 1} className={styles.next} onClick={next} />
          </Col>
        </Row>
      </div>
    </div>
  ) : (
    <div>{t('dataset.asset.empty')}</div>
  )
}

export default Asset
