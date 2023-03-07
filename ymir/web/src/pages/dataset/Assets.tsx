import { useCallback, useEffect, useRef, useState } from 'react'
import type { FC } from 'react'
import { useLocation, useParams } from 'umi'
import { Pagination, Row, Col, Button, Space, Card, Tag, Modal, Select } from 'antd'

import t from '@/utils/t'
import { randomBetween } from '@/utils/number'
import useRequest from '@/hooks/useRequest'

import Breadcrumbs from '@/components/common/breadcrumb'
import KeywordSelector from '@/components/form/KeywordFilter'
import EvaluationSelector from '@/components/form/EvaluationSelector'
import Asset from './components/Asset'
import List from './components/AssetList'

import styles from './assets.less'
import DatasetInfo from './components/DatasetInfo'
import ListColumnCountSelect from './components/ListColumnCountSelect'
import ListVisualSelect from './components/ListVisualSelect'
import VisualModes from './components/VisualModes'
import { isDetection } from '@/constants/objectType'

type IndexType = {
  hash: string
  index: number
  asset?: YModels.Asset
}

const Dataset: FC = () => {
  const { id: pid, did: id } = useParams<{ id: string; did: string; type: string }>()
  const location = useLocation()
  const type = location.hash.replace(/^#/, '')
  const initQuery = {
    pid,
    annoType: type === 'pred' ? 2 : 1,
    id,
    offset: 0,
    limit: 20,
  }
  const [filterParams, setFilterParams] = useState<YParams.AssetQueryParams>(initQuery)
  const [currentPage, setCurrentPage] = useState(1)
  const [assetVisible, setAssetVisible] = useState(false)
  const [currentAsset, setCurrentAsset] = useState<IndexType>({
    hash: '',
    index: 0,
  })
  const [columns, setColumns] = useState(5)
  const [isPred, setPred] = useState(false)
  const [mode, setMode] = useState<VisualModes>(VisualModes.Gt)
  const { data: dataset, run: getDataset } = useRequest<YModels.Dataset>('dataset/getDataset', {
    loading: false,
  })
  const { data: prediction, run: getPrediction } = useRequest<YModels.Dataset>('prediction/getPrediction', {
    loading: false,
  })
  const [current, setCurrent] = useState<YModels.Prediction | YModels.Dataset>()
  const { data: { items: assets, total } = { items: [], total: 0 }, run: getAssets } = useRequest<
    YStates.List<YModels.Asset>,
    [
      YParams.AssetQueryParams & {
        datasetKeywords?: string[]
      },
    ]
  >('asset/getAssets')

  useEffect(() => {
    ;(type === 'pred' ? getPrediction : getDataset)({ id, verbose: true, force: true })
  }, [id])

  useEffect(() => {
    const isPred = type === 'pred'
    setPred(isPred)
    setMode(isPred ? VisualModes.All : VisualModes.Gt)
  }, [type])

  useEffect(() => {
    setCurrent(isPred ? prediction : dataset)
  }, [dataset, prediction, type])

  useEffect(() => {
    const { offset = 0, limit = 20 } = filterParams
    setCurrentPage(offset / limit + 1)
    current?.id && filter(filterParams)
    console.log('current:', current)
  }, [current, filterParams])

  const filterKw = ({ type, selected }: { type: string; selected?: string[] }) => {
    if (!selected?.length && !filterParams.keywords?.length) {
      return
    }
    setFilterParams((params) => ({
      ...params,
      type,
      keywords: selected,
      offset: initQuery.offset,
    }))
  }

  const filterPage = (page: number, pageSize: number) => {
    setCurrentPage(page)
    const limit = pageSize
    const offset = limit * (page - 1)
    setFilterParams((params) => ({ ...params, offset, limit }))
  }
  const filter = (params: YParams.AssetQueryParams) => {
    getAssets({ ...params, datasetKeywords: dataset?.keywords })
  }
  const goAsset = (asset: YModels.Asset, hash: string, current: number) => {
    const index = (filterParams.offset || 0) + current
    setCurrentAsset({ asset, hash, index })
    setAssetVisible(true)
  }

  const randomPage = () => {
    const { limit = 20, offset = 0 } = filterParams
    setCurrentPage(offset / limit + 1)
    const page = randomBetween(Math.ceil(total / limit), 1, currentPage)
    filterPage(page, limit)
  }

  const updateFilterParams = (value: string | string[] | number, field: string) => {
    setFilterParams((query) => ({
      ...query,
      [field]: value,
      offset: initQuery.offset,
    }))
  }

  const reset = () => {
    setFilterParams({ ...initQuery, keywords: [] })
  }

  const randomPageButton = (
    <Button type="primary" onClick={randomPage}>
      {t('dataset.detail.randompage.label')}
    </Button>
  )

  const renderTitle = (
    <Row className={styles.labels}>
      <Col flex={1}>
        <DatasetInfo dataset={current} pred={isPred} />
      </Col>
      <Col>
        <ListColumnCountSelect value={columns} onChange={setColumns} />
      </Col>
      <Col span={24} style={{ fontSize: 14, textAlign: 'right', marginTop: 10 }}>
        <Space size={20} wrap={true} style={{ textAlign: 'left' }}>
          <ListVisualSelect value={mode} style={{ width: 200 }} pred={isPred} seg={!isDetection(current?.type)} onChange={setMode} />
          {isPred && current?.evaluated ? (
            <EvaluationSelector value={filterParams.cm} onChange={({ target }) => updateFilterParams(target.value, 'cm')} />
          ) : null}
          <KeywordSelector onChange={filterKw} dataset={current} />
        </Space>
      </Col>
    </Row>
  )

  const assetDetail = (
    <Modal
      className={styles.assetDetail}
      destroyOnClose
      title={t('dataset.asset.title')}
      visible={assetVisible}
      onCancel={() => setAssetVisible(false)}
      centered
      width={'100%'}
      footer={null}
    >
      {currentAsset.asset ? (
        <Asset
          id={id}
          pred={isPred}
          asset={currentAsset.asset}
          datasetKeywords={current?.keywords}
          filters={filterParams}
          filterKeyword={assetVisible ? filterParams.keywords : undefined}
          index={currentAsset.index}
          total={total}
          dataset={current}
        />
      ) : null}
    </Modal>
  )

  return (
    <div className={styles.datasetDetail}>
      <Breadcrumbs />
      {assetDetail}
      <Card className="list" title={renderTitle}>
        <List
          list={assets}
          goAsset={goAsset}
          columns={columns}
          mode={mode}
          pager={
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
                showTotal={(total, range) => t('dataset.detail.pager.total', { total })}
                onChange={filterPage}
              />
              {randomPageButton}
            </Space>
          }
        />
      </Card>
    </div>
  )
}

export default Dataset
