import { ComponentProps, useEffect, useState } from 'react'
import type { FC } from 'react'
import { useLocation, useParams } from 'umi'
import { Pagination, Button, Space, Card } from 'antd'

import t from '@/utils/t'
import { randomBetween } from '@/utils/number'
import useRequest from '@/hooks/useRequest'
import useModal from '@/hooks/useModal'

import Breadcrumbs from '@/components/common/breadcrumb'
import Asset from './components/Asset'
import List from './components/AssetList'
import AssetsTitle, { FormValues } from './components/AssetsTitle'

import styles from './assets.less'

import { List as ListType } from '@/models/typings/common'
import { ValueType } from '@/components/form/KeywordFilter'

type IndexType = {
  hash: string
  index: number
  asset?: YModels.Asset
}

const Dataset: FC = () => {
  const { id: pid, did, prid } = useParams<{ id: string; did: string; type: string, prid?: string }>()
  const location = useLocation()
  const isPred = !!prid
  const id = prid ? prid : did
  const initQuery = {
    pid,
    annoType: isPred ? 2 : 1,
    id,
    offset: 0,
    limit: 20,
  }
  const [filterParams, setFilterParams] = useState<YParams.AssetQueryParams>(initQuery)
  const [currentPage, setCurrentPage] = useState(1)
  const [currentAsset, setCurrentAsset] = useState<IndexType>({
    hash: '',
    index: 0,
  })
  const { data: dataset, run: getDataset } = useRequest<YModels.Dataset>('dataset/getDataset', {
    loading: false,
  })
  const { data: prediction, run: getPrediction } = useRequest<YModels.Dataset>('prediction/getPrediction', {
    loading: false,
  })
  const [current, setCurrent] = useState<YModels.Prediction | YModels.Dataset>()
  const { data: { items: assets, total } = { items: [], total: 0 }, run: getAssets } = useRequest<
    ListType<YModels.Asset>,
    [
      YParams.AssetQueryParams & {
        datasetKeywords?: string[]
      },
    ]
  >('asset/getAssets')
  const [AssetModal, showAssetModal] = useModal<ComponentProps<typeof Asset>>(Asset, {
    width: '100%',
    className: styles.assetDetail,
    title: t('dataset.asset.title'),
  })
  const [filterValues, setFilterValues] = useState<FormValues>({})

  useEffect(() => {
    ;(isPred ? getPrediction : getDataset)({ id, verbose: true, force: true })
  }, [id])

  useEffect(() => {
    setCurrent(isPred ? prediction : dataset)
  }, [dataset, prediction, isPred])

  useEffect(() => {
    const { offset = 0, limit = 20 } = filterParams
    setCurrentPage(offset / limit + 1)
    current?.id && filter(filterParams)
  }, [current, filterParams])

  useEffect(() => {
    filterValues.keywords && filterKw(filterValues.keywords)
  }, [filterValues.keywords])

  useEffect(() => {
    setFilterParams((query) => ({
      ...query,
      cm: filterValues.evaluation,
      offset: initQuery.offset,
    }))
  }, [filterValues.evaluation])

  const filterKw = ({ type, selected }: ValueType) => {
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
    // setAssetVisible(true)
    showAssetModal()
  }

  const randomPage = () => {
    const { limit = 20, offset = 0 } = filterParams
    setCurrentPage(offset / limit + 1)
    const page = randomBetween(Math.ceil(total / limit), 1, currentPage)
    filterPage(page, limit)
  }

  const filterChange = (values: FormValues) => {
    setFilterValues(values)
  }

  const randomPageButton = (
    <Button type="primary" onClick={randomPage}>
      {t('dataset.detail.randompage.label')}
    </Button>
  )

  return (
    <div className={styles.datasetDetail}>
      <Breadcrumbs />
      <AssetModal
        id={id}
        pred={isPred}
        asset={currentAsset.asset}
        datasetKeywords={current?.keywords}
        filters={filterParams}
        filterKeyword={filterParams?.keywords}
        index={currentAsset.index}
        total={total}
        dataset={current}
      />
      <Card className="list" title={<AssetsTitle isPred={isPred} current={current} onChange={filterChange} />}>
        <List
          list={assets}
          goAsset={goAsset}
          columns={filterValues.columns}
          mode={filterValues.mode}
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
