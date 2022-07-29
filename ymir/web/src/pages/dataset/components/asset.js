
import { useHistory, useParams } from "react-router"
import React, { useEffect, useRef, useState } from "react"
import { Button, Card, Col, Descriptions, Row, Tag, Space } from "antd"
import { connect } from "dva"

import { getDateFromTimestamp } from "@/utils/date"
import t from "@/utils/t"
import { randomBetween } from "@/utils/number"

import Hash from "@/components/common/hash"
import AssetAnnotation from "@/components/dataset/assetAnnotation"
import GtSelector from "@/components/form/gtSelector"

import styles from "./asset.less"
import { ArrowRightIcon, NavDatasetIcon, EyeOffIcon, EyeOnIcon } from '@/components/common/icons'
import { LeftOutlined, RightOutlined } from '@ant-design/icons'

const { CheckableTag } = Tag

function Asset({ id, asset: cache, filterKeyword, getAsset, getAssetsOfDataset, index = 0, total = 0 }) {
  const history = useHistory()
  const [asset, setAsset] = useState({})
  const [current, setCurrent] = useState('')
  const [showAnnotations, setShowAnnotations] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [currentIndex, setCurrentIndex] = useState(null)
  const [assetHistory, setAssetHistory] = useState([])
  const [evaluation, setEvaluation] = useState({})
  const [colors, setColors] = useState({})

  useEffect(() => {
    setAsset({})
    index > -1 && setCurrentIndex({ index, keyword: filterKeyword })
  }, [index, filterKeyword])

  useEffect(() => {
    if (currentIndex !== null) {
      fetchAssetHash()
      setAssetHistory(history => [...history, currentIndex])
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
    setSelectedKeywords(asset.keywords)
  }, [asset])

  useEffect(() => {
    if (!cache) {
      return
    }
    const { annotations } = cache
    setColors(annotations.reduce((prev, annotation) => ({ ...prev, [annotation.keyword]: annotation.color }), {}))
  }, [cache])

  useEffect(() => {
    const keywordFilter = annotation => selectedKeywords.indexOf(annotation.keyword) >= 0
    const evaluationFilter = annotation => !annotation.cm || evaluation[annotation.cm]
    const filters = annotation => keywordFilter(annotation) && evaluationFilter(annotation)
    const visibleAnnotations = (asset.annotations || []).filter(filters)
    setShowAnnotations(visibleAnnotations)
  }, [selectedKeywords, evaluation, asset])

  async function fetchAsset() {
    const result = await getAsset(id, current)
    const corretColor = (annotations = []) => annotations.map(anno => ({ ...anno, color: colors[anno.keyword]}))
    setAsset({...result, annotations: corretColor(result.annotations)})
  }

  async function fetchAssetHash() {
    const result = await getAssetsOfDataset({ id, keyword: currentIndex.keyword, offset: currentIndex.index, limit: 1 })
    if (result?.items) {
      const ass = result.items[0]
      setCurrent(ass.hash)
      fetchAsset()
    }
  }

  function next() {
    setCurrentIndex(cu => ({ ...cu, index: cu.index + 1 }))
  }

  function prev() {
    setCurrentIndex(cu => ({ ...cu, index: cu.index - 1 }))
  }

  function random() {
    setCurrentIndex(cu => ({ ...cu, index: randomBetween(0, total - 1, cu.index) }))
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
    const selected = checked
      ? [...selectedKeywords, tag]
      : selectedKeywords.filter((k) => k !== tag)
    setSelectedKeywords(selected)
  }

  function toggleAnnotation() {
    setSelectedKeywords(selectedKeywords.length ? [] : asset.keywords)
  }

  function filterAnnotations(checkeds) {
    setEvaluation(checkeds)
  }

  return asset.hash ? (
    <div className={styles.asset}>
      <div className={styles.info}>
        <Row className={styles.infoRow} align="center" wrap={false}>
          <Col flex={'20px'} style={{ alignSelf: 'center' }}><LeftOutlined hidden={currentIndex.index <= 0} className={styles.prev} onClick={prev} /></Col>
          <Col flex={1} className={`${styles.asset_img} scrollbar`}>
            {asset.annotations ? (
              <AssetAnnotation
                url={asset.url}
                keywords={asset.keywords}
                data={showAnnotations}
              // toggleHandle={toggleAnnotation}
              />
            ) : null}
          </Col>
          <Col span={6} className={styles.asset_info}>
            <Card
              title={<><NavDatasetIcon /> {t("dataset.asset.info")}</>}
              bordered={false}
              className='noShadow'
              style={{ marginRight: 20 }}
              headStyle={{ paddingLeft: 0 }}
              bodyStyle={{ padding: "20px 0" }}
            >
              <Descriptions
                bordered
                column={2}
                contentStyle={{ flexWrap: 'wrap', padding: '10px' }}
                labelStyle={{ justifyContent: 'flex-end', padding: '10px' }}
              >
                <Descriptions.Item label={t("dataset.asset.info.id")} span={2}>
                  <Hash value={current} />
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.width")}>
                  {asset.metadata?.width}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.height")}>
                  {asset.metadata?.height}
                </Descriptions.Item>
                {asset.size ? (
                  <Descriptions.Item label={t("dataset.asset.info.size")}>
                    {asset.size}
                  </Descriptions.Item>
                ) : null}
                <Descriptions.Item label={t("dataset.asset.info.channel")} span={asset.size ? 1 : 2}>
                  {asset.metadata?.channel}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.timestamp")} span={2}>
                  {getDateFromTimestamp(asset.metadata?.timestamp)}
                </Descriptions.Item>
                <Descriptions.Item label={t("dataset.asset.info.keyword")} span={2}>
                  <Row>
                    <Col flex={1}>
                      {asset.keywords?.map((keyword, i) => (
                        <CheckableTag
                          checked={selectedKeywords.indexOf(keyword) > -1}
                          onChange={(checked) => changeKeywords(keyword, checked)}
                          className={'ant-tag-' + colors[keyword]}
                          key={i}
                        >
                          {keyword}
                        </CheckableTag>
                      ))}
                    </Col>
                    <Col>
                      {selectedKeywords.length ?
                        <EyeOnIcon onClick={toggleAnnotation} title={t("dataset.asset.annotation.hide")} /> :
                        <EyeOffIcon onClick={toggleAnnotation} title={t("dataset.asset.annotation.show")} />}
                    </Col>
                  </Row>
                </Descriptions.Item>
              </Descriptions>
              <div className={styles.filter}>
                <h3><NavDatasetIcon /> {t("dataset.asset.filters.title")}</h3>
                <GtSelector layout='vertical' onChange={filterAnnotations} />
              </div>
            </Card>
            <Space className={styles.random}>
              <Button
                type="primary"
                style={{ marginTop: 20 }}
                onClick={random}
              >
                {t("dataset.asset.random")}
              </Button>
              <Button
                className={styles.back}
                type="primary"
                style={{ marginTop: 20 }}
                onClick={back}
              >
                {t("dataset.asset.back")}
              </Button></Space>
          </Col>
          <Col style={{ alignSelf: 'center' }} flex={'20px'}><RightOutlined hidden={currentIndex.index >= total - 1} className={styles.next} onClick={next} /></Col>
        </Row>
      </div>
    </div>
  ) : (
    <div>{t("dataset.asset.empty")}</div>
  )
}

const actions = (dispatch) => {
  return {
    getAsset(id, hash) {
      return dispatch({
        type: "dataset/getAsset",
        payload: { id, hash },
      })
    },
    getAssetsOfDataset(payload) {
      return dispatch({
        type: "dataset/getAssetsOfDataset",
        payload,
      })
    },
  }
}

export default connect(null, actions)(Asset)
