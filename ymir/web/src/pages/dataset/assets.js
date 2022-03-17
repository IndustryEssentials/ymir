import React, { useEffect, useState } from "react"
import { useParams, useHistory } from "umi"
import { connect } from "dva"
import { Select, Pagination, Image, Row, Col, Button, Space, Card, Descriptions, Tag, Modal } from "antd"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomBetween, percent } from '@/utils/number'
import Asset from "./components/asset"
import styles from "./assets.less"
import { ScreenIcon, TaggingIcon, TrainIcon, VectorIcon, WajueIcon, } from "@/components/common/icons"

const { Option } = Select

function rand(n, m, exclude) {
  const result = Math.min(m, n) + Math.floor(Math.random() * Math.abs(m - n))

  if (result === exclude) {
    return rand(n, m, exclude)
  }
  if (result < 0) {
    return 0
  }
  return result
}

const Dataset = ({ getDataset, getAssetsOfDataset }) => {
  const { id } = useParams()
  const initQuery = {
    id,
    keyword: null,
    offset: 0,
    limit: 20,
  }
  const history = useHistory()
  const [filterParams, setFilterParams] = useState(initQuery)
  const [dataset, setDataset] = useState({ id })
  const [assets, setAssets] = useState([])
  const [total, setTotal] = useState(0)
  const [keywords, setKeywords] = useState([])
  const [currentPage, setCurrentPage] = useState(1)
  const [assetVisible, setAssetVisible] = useState(false)
  const [currentAsset, setCurrentAsset] = useState({
    hash: null,
    index: 0,
  })

  useEffect(async () => {
    const data = await getDataset(id)
    if (data) {
      setDataset(data)
    }
  }, [id])

  useEffect(() => {
    setCurrentPage((filterParams.offset / filterParams.limit) + 1)
    filter(filterParams)
  }, [filterParams])

  const filterKw = (kw) => {
    const keyword = kw ? kw : undefined
    setFilterParams((params) => ({
      ...params,
      keyword,
      offset: initQuery.offset,
    }))
  }
  const filterPage = (page, pageSize) => {
    setCurrentPage(page)
    const limit = pageSize
    const offset = limit * (page - 1)
    setFilterParams((params) => ({ ...params, offset, limit }))
  }
  const filter = async (param) => {
    setAssets([])
    const { items, keywords, total } = await getAssetsOfDataset(param)
    setTotal(total)
    setAssets(items)
    setKeywords(Object.keys(keywords).map((key) => ({ key, count: keywords[key] })))
  }
  const goAsset = (hash, index) => {
    setCurrentAsset({ hash, index: filterParams.offset + index})
    setAssetVisible(true)
  }

  const randomPage = () => {
    const { limit, offset } = filterParams
    setCurrentPage(offset / limit + 1)
    const page = randomBetween(Math.ceil(total / limit), 1, currentPage)
    filterPage(page, limit)
  }

  const getRate = (count) => {
    return percent(count / dataset.asset_count)
  }

  const randomPageButton = (
    <Button type="primary" onClick={randomPage}>
      {t("dataset.detail.randompage.label")}
    </Button>
  )

  const renderList = (list, row = 5) => {
    let r = 0, result = []
    while (r < list.length) {
      result.push(list.slice(r, r + row))
      r += row
    }

    return result.map((rows, index) => (
      <Row gutter={10} wrap={false} key={index} className={styles.dataset_container}>
        {rows.map((asset, rowIndex) => (
          <Col flex={100 / row + '%'} key={asset.hash} className={styles.dataset_item}>
            <div
              className={styles.dataset_img}
              onClick={() => goAsset(asset.hash, index * row + rowIndex)}
            >
              <img
                src={asset.url}
                style={{ width: "auto", maxWidth: "100%", maxHeight: "100%" }}
              />
              <span
                className={styles.item_keywords_count}
                title={asset.keywords.join(",")}
              >
                {t("dataset.detail.assets.keywords.total", {
                  total: asset.keywords.length,
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
    ))
  }

  const renderTitle = <Row className={styles.labels}>
    <Col flex={1}>
      <Space>
        <strong>{dataset.name}</strong>
        <span>{t("dataset.detail.pager.total", { total: total + '/' + dataset.assetCount })}</span>
      </Space>
    </Col>
    <Col>
      <span>{t("dataset.detail.keyword.label")}</span>
      <Select
        showSearch
        defaultValue={0}
        style={{ width: 160 }}
        onChange={filterKw}
        filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
      >
        <Option value={0} key="all">
          {t("common.all")}
        </Option>
        {keywords.map((kw) => (
          <Option value={kw.key} key={kw.key} title={`${kw.key} (${kw.count})`}>
            {kw.key} ({kw.count}, {getRate(kw.count)})
          </Option>
        ))}
      </Select>
    </Col>
  </Row>

  const assetDetail = <Modal className={styles.assetDetail} 
    title={t('dataset.asset.title')} visible={assetVisible} onCancel={() => setAssetVisible(false)}
    width={null} footer={null}>
    <Asset id={id} datasetKeywords={dataset.keywords} filterKeyword={assetVisible ? filterParams.keyword : null} index={currentAsset.index} total={total} />
  </Modal>

  return (
    <div className={styles.datasetDetail}>
      <Breadcrumbs />
      {assetDetail}
      <div className={styles.actions}>
        <Space>
          <Button
            hidden={!dataset.keyword_count}
            icon={<ScreenIcon className={styles.addBtnIcon} />}
            onClick={() => history.push(`/home/task/filter/${id}`)}
          >{t('dataset.detail.action.filter')} </Button>
          <Button
            icon={<TrainIcon className={styles.addBtnIcon} />}
            type='primary'
            onClick={() => history.push(`/home/task/train/${id}`)}
          >{t('dataset.detail.action.train')}</Button>
          <Button icon={<VectorIcon className={styles.addBtnIcon} />}
            onClick={() => history.push(`/home/task/mining/${id}`)}>{t('dataset.detail.action.mining')}</Button>
          <Button icon={<TaggingIcon className={styles.addBtnIcon} />}
            onClick={() => history.push(`/home/task/label/${id}`)}>{t('dataset.detail.action.label')}</Button>
        </Space>
      </div>
      <Card className={styles.list} title={renderTitle}>

        {renderList(assets)}
        <Space className={styles.pagi}>
          <Pagination
            key={'pager'}
            className={styles.pager}
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

const mapStateToProps = (state) => {
  return {
    logined: state.user.logined,
  }
}

const mapDispatchToProps = (dispatch) => {
  return {
    getDataset(payload) {
      return dispatch({
        type: "dataset/getDataset",
        payload,
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

export default connect(mapStateToProps, mapDispatchToProps)(Dataset)
