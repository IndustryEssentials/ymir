import { Popover, TableColumnType } from 'antd'
import { ReactNode } from 'react'

import t from '@/utils/t'
import { humanize, toFixed } from '@/utils/number'
import { ObjectType } from '@/constants/project'
import VersionName from '@/components/result/VersionName'

type AnnotationType = 'gt' | 'pred'
type ChartConfigType = {
  label: string
  sourceField: string
  totalField: string
  xUnit?: string
  renderEachX?: (x: any) => string
  color?: string[]
  customOptions?: {
    [key: string]: any
  }
  isXUpperLimit?: boolean
  annoType?: boolean
  xType?: string
  getSource?: (dataset: YModels.DatasetAnalysis) => Array<{ [key: string]: any }>
}
type ColumnType = TableColumnType<YModels.DatasetAnalysis>

const charts: { [key: string]: ChartConfigType } = {
  assetHWRatio: {
    label: 'dataset.analysis.title.asset_hw_ratio',
    sourceField: 'assetHWRatio',
    totalField: 'assetCount',
    color: ['#36CBCB', '#E8B900'],
  },
  assetArea: {
    label: 'dataset.analysis.title.asset_area',
    sourceField: 'assetArea',
    totalField: 'assetCount',
    xUnit: 'PX',
    renderEachX: (x: number) => `${x / 10000}W`,
    color: ['#36CBCB', '#F2637B'],
  },
  assetQuality: {
    label: 'dataset.analysis.title.asset_quality',
    sourceField: 'assetQuality',
    totalField: 'assetCount',
    color: ['#36CBCB', '#10BC5E'],
    isXUpperLimit: true,
  },
  areaRatio: {
    label: 'dataset.analysis.title.anno_area_ratio',
    sourceField: 'areaRatio',
    totalField: 'total',
    customOptions: {
      tooltipLable: 'dataset.analysis.bar.anno.tooltip',
    },
    color: ['#10BC5E', '#E8B900'],
    isXUpperLimit: true,
  },
  keywords: {
    label: 'dataset.analysis.title.keyword_ratio',
    sourceField: 'keywords',
    totalField: 'total',
    customOptions: {
      tooltipLable: 'dataset.analysis.bar.anno.tooltip',
    },
    color: ['#2CBDE9', '#E8B900'],
    xType: 'attribute',
  },
  keywordArea: {
    label: 'dataset.analysis.title.keyword_area',
    sourceField: 'keywordArea',
    totalField: 'total',
    customOptions: {
      tooltipLable: 'dataset.analysis.bar.anno.tooltip',
    },
    color: ['#2CBDE9', '#E8B900'],
    xType: 'attribute',
  },
  instanceArea: {
    label: 'dataset.analysis.title.instance_area',
    sourceField: 'instanceArea',
    totalField: 'totalArea',
    xUnit: 'px',
    isXUpperLimit: true,
    color: ['#10BC5E', '#F2637B'],
  },
  crowdedness: {
    label: 'dataset.analysis.title.crowdedness',
    sourceField: 'crowdedness',
    totalField: 'assetCount',
    isXUpperLimit: true,
    color: ['#10BC5E', '#F2637B'],
  },
}

const getAnnotations = (item: YModels.DatasetAnalysis, type: AnnotationType) => item[type]

const getColumns = (keys: string[], type: AnnotationType) => {
  const columns: { [key: string]: ColumnType } = {
    name: {
      title: title('dataset.analysis.column.name'),
      render: (_, record) => <VersionName result={record} />,
    },
    labeled: {
      title: title('dataset.analysis.column.labelled'),
      render: (_, record) => {
        const anno = getAnnotations(record, type)
        const labeled = record.assetCount - anno.negative
        return renderPop(labeled)
      },
      width: 80,
    },
    assetCount: {
      title: title('dataset.analysis.column.assets.count'),
      render: (assetCount) => renderPop(assetCount),
    },
    keywordsCount: {
      title: title('dataset.analysis.column.keywords.count'),
      render: (_, record) => Object.keys(getAnnotations(record, type)).length,
    },
    averageKeywordsCount: {
      title: title('dataset.analysis.column.keywords.count.average'),
      render: (_, record) => toFixed(getAnnotations(record, type).average),
    },
    annotationsCount: {
      title: title('dataset.analysis.column.annotations.total'),
      render: (_, record) => {
        const count = getAnnotations(record, type).total
        return renderPop(count)
      },
    },
    averageAnnotationsCount: {
      title: title('dataset.analysis.column.annotations.average'),
      render: (_, record) => toFixed(getAnnotations(record, type).average),
    },
    annotationsAreaTotal: {
      title: title('dataset.analysis.column.annotations.area.total'),
      render: (_, record) => unit(getAnnotations(record, type).totalArea),
    },
    averageAnnotationsArea: {
      title: title('dataset.analysis.column.annotations.area.average'),
      render: (_, record) => {
        const total = getAnnotations(record, type).average
        return unit(toFixed(total / record.assetCount))
      },
    },
    instanceCount: {
      title: title('dataset.analysis.column.instances.total'),
      render: (_, record) => renderPop(getAnnotations(record, type).totalInstanceCount),
    },
    averageInstanceCount: {
      title: title('dataset.analysis.column.instances.average'),
      render: (_, record) => {
        const total = getAnnotations(record, type).totalInstanceCount
        return toFixed(total / record.assetCount)
      },
    },
    cksCount: {
      title: title('dataset.analysis.column.cks.count'),
      render: (text, record) =>  record.cks?.subKeywordsTotal || 0,
    },
  }
  return keys.map((key) => ({ ...columns[key], dataIndex: key, ellipsis: true, align: 'center' }))
}

function renderPop(num: number) {
  const label = humanize(num)
  return (
    <Popover content={num}>
      <span>{label}</span>
    </Popover>
  )
}

function unit(value?: string | number, u = 'px', def: string | number = 0) {
  return value ? value + u : def + u
}

function title(str = '') {
  return <strong>{t(str)}</strong>
}

const getTableColumns = (objectType: YModels.ObjectType, annotationType: AnnotationType) => {
  const keys = (count: string, average: string) => ['name', 'labeled', 'assetCount', 'keywordsCount', 'averageKeywordsCount', count, average, 'cksCount']
  const maps = {
    [ObjectType.ObjectDetection]: keys('annotationsCount', 'averageAnnotationsCount'),
    [ObjectType.SemanticSegmentation]: keys('annotationsAreaTotal', 'averageAnnotationsArea'),
    [ObjectType.InstanceSegmentation]: keys('instanceCount', 'averageInstanceCount'),
  }
  return getColumns(maps[objectType], annotationType)
}

// todo 场景复杂度
const getCharts = (annotationType?: AnnotationType, objectType?: YModels.ObjectType) => {
  const maps = {
    [ObjectType.ObjectDetection]: ['keywords', 'areaRatio'],
    [ObjectType.SemanticSegmentation]: ['keywords', 'keywordArea'],
    [ObjectType.InstanceSegmentation]: ['keywords', 'crowdedness', 'instanceArea', 'keywordArea'],
  }
  const assetCharts = ['assetHWRatio', 'assetQuality', 'assetArea']
  const keys = objectType ? maps[objectType] : assetCharts
  return keys.map((key) => ({
    ...charts[key],
    getSource: (dataset: YModels.DatasetAnalysis) => (annotationType ? getAnnotations(dataset, annotationType) : dataset),
  }))
}

export const getConfigByAnnotationType = (objectType: YModels.ObjectType, annotationType: AnnotationType) => {
  return {
    tableColumns: getTableColumns(objectType, annotationType),
    assetChartConfig: getCharts(),
    annotationChartConfig: getCharts(annotationType, objectType),
  }
}
