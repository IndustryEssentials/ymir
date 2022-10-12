import React, { useCallback, useEffect, useRef, useState } from "react"
import { useParams } from "umi"
import { Select, Pagination, Row, Col, Button, Space, Card, Tag, Modal } from "antd"

import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import { randomBetween, percent } from '@/utils/number'

import Breadcrumbs from "@/components/common/breadcrumb"
import Asset from "./components/asset"
import styles from "./assets.less"
import GtSelector from "@/components/form/gtSelector"
import ImageAnnotation from "@/components/dataset/imageAnnotation"
import useWindowResize from "@/hooks/useWindowResize"
import KeywordSelector from "./components/keywordSelector"
import EvaluationSelector from "@/components/form/evaluationSelector"

const { Option } = Select

const Dataset = () => {
  const { id: pid, did: id } = useParams()
  const initQuery = {
    id,
    keywords: [],
    offset: 0,
    limit: 20,
  }
  const [filterParams, setFilterParams] = useState(initQuery)
  const [currentPage, setCurrentPage] = useState(1)
  const [assetVisible, setAssetVisible] = useState(false)
  const [currentAsset, setCurrentAsset] = useState({
    hash: null,
    index: 0,
  })
  const listRef = useRef(null)
  const windowWidth = useWindowResize()
  const [dataset, getDataset] = useFetch('dataset/getDataset', {})
  const [{ items: assets, total }, getAssets, setAssets] = useFetch('dataset/getAssetsOfDataset', { items: [], total: 0 })

  useEffect(() => {
    getDataset({ id, verbose: true })
  }, [id])

  useEffect(() => {
    setCurrentPage((filterParams.offset / filterParams.limit) + 1)
    dataset.id && filter(filterParams)
  }, [dataset, filterParams])

  const filterKw = ({ type, selected }) => {
    const s = selected.map(item => Array.isArray(item) ? item.join(':') : item)
    if (s.length || (!s.length && filterParams.keywords.length > 0)) {
      setFilterParams((params) => ({
        ...params,
        type,
        keywords: s,
        offset: initQuery.offset,
      }))
    }
  }

  const filterPage = (page, pageSize) => {
    setCurrentPage(page)
    const limit = pageSize
    const offset = limit * (page - 1)
    setFilterParams((params) => ({ ...params, offset, limit }))
  }
  const filter = (param) => {
    getAssets({ ...param, datasetKeywords: dataset?.keywords })
  }
  const goAsset = (asset, hash, index) => {
    setCurrentAsset({ asset, hash, index: filterParams.offset + index })
    setAssetVisible(true)
  }

  const randomPage = () => {
    const { limit, offset } = filterParams
    setCurrentPage(offset / limit + 1)
    const page = randomBetween(Math.ceil(total / limit), 1, currentPage)
    filterPage(page, limit)
  }

  const filterAnnotations = useCallback(annotations => {
    const cm = filterParams.cm || []
    const annoType = filterParams.annoType || []
    const gtFilter = annotation => !annoType.length || annoType.some(selected => selected === 'gt' ? annotation.gt : !annotation.gt)
    const evaluationFilter = annotation => !cm.length || cm.includes(annotation.cm)
    return annotations.filter(annotation => gtFilter(annotation) && evaluationFilter(annotation))
  }, [filterParams.cm, filterParams.annoType])

  const updateFilterParams = (value, field) => {
    if (value?.length || (filterParams[field]?.length && !value?.length)) {
      setFilterParams(query => ({
        ...query,
        [field]: value,
        offset: initQuery.offset,
      }))
    }
  }

  const reset = () => {
    setFilterParams(initQuery)
  }

  const randomPageButton = (
    <Button type="primary" onClick={randomPage}>
      {t("dataset.detail.randompage.label")}
    </Button>
  )

  const renderList = useCallback((list, row = 5) => {
    let r = 0, result = []
    while (r < list.length) {
      result.push(list.slice(r, r + row))
      r += row
    }

    return result.map((rows, index) => {
      const h = listRef.current?.clientWidth / rows.reduce((prev, row) => {
        return (prev + row.metadata.width / row.metadata.height)
      }, 0)

      return (
        <Row gutter={4} wrap={false} key={index} className={styles.dataset_container}>
          {rows.map((asset, rowIndex) => (
            <Col style={{ height: h }} key={rowIndex} className={styles.dataset_item}>
              <div
                className={styles.dataset_img}
                onClick={() => goAsset(asset, asset.hash, index * row + rowIndex)}
              >
                <ImageAnnotation url={asset.url} data={asset.annotations} filters={filterAnnotations} />
                <span
                  className={styles.item_keywords_count}
                  title={asset?.keywords.join(",")}
                >
                  {t("dataset.detail.assets.keywords.total", {
                    total: asset?.keywords?.length,
                  })}
                </span>
                <span className={styles.item_keywords}>
                  {asset.keywords.slice(0, 4).map(key => <Tag className={styles.item_keyword} key={key} title={key}>{key}</Tag>)}
                  {asset.keywords.length > 4 ? <Tag className={styles.item_keyword} style={{ width: '10px' }}>...</Tag> : null}
                </span>
              </div>
            </Col>
          ))}
        </Row>
      )
    }
    )
  }, [windowWidth, filterParams])

  const renderTitle = <Row className={styles.labels}>
    <Col span={12}>
      <Space>
        <strong>{dataset.name} {dataset.versionName}</strong>
        <span>{t("dataset.detail.pager.total", { total: total + '/' + dataset.assetCount })}</span>
        {dataset?.inferClass ? <div>{t('dataset.detail.infer.class')}{dataset?.inferClass?.map(cls => <Tag key={cls}>{cls}</Tag>)}</div> : null}
      </Space>
    </Col>
    <Col span={12}>
      <Space size={10} wrap={true}>
        <GtSelector layout='inline' value={filterParams.annoType} onChange={checked => updateFilterParams(checked, 'annoType')} />
        <EvaluationSelector value={filterParams.cm} onChange={checked => updateFilterParams(checked, 'cm')} labelAlign={'right'} />
        <KeywordSelector value={filterParams.keywords} onChange={filterKw} dataset={dataset} labelAlign={'right'} />
        <Button onClick={reset}>{t('common.reset')}</Button>
      </Space>
    </Col>
  </Row>

  const assetDetail = <Modal className={styles.assetDetail} destroyOnClose
    title={t('dataset.asset.title')} visible={assetVisible} onCancel={() => setAssetVisible(false)}
    width={null} footer={null}>
    <Asset
      id={id}
      asset={currentAsset.asset}
      datasetKeywords={dataset.keywords}
      filters={filterParams}
      filterKeyword={assetVisible ? filterParams.keywords : null}
      index={currentAsset.index} total={total}
    />
  </Modal>

  return (
    <div className={styles.datasetDetail}>
      <Breadcrumbs />
      {assetDetail}
      <Card className='list' title={renderTitle}>
        <div className={styles.listContainer} ref={listRef}>
          {renderList(assets)}
        </div>
        <Space className={styles.pagi}>
          <Pagination
            key={'pager'}
            className={`pager ${styles.pager}`}
            showQuickJumper
            showSizeChanger
            defaultCurrent={1}
            current={currentPage}
            defaultPageSize={20}
            total={total}
            showTotal={(total, range) =>
              t("dataset.detail.pager.total", { total })
            }
            onChange={filterPage}
          />
          {randomPageButton}
        </Space>
      </Card>
    </div>
  )
}

export default Dataset
