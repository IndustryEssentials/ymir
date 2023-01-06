import { Popover, TableColumnType } from 'antd'
import { ReactNode } from 'react'

import t from '@/utils/t'
import { humanize } from '@/utils/number'
import { ObjectType } from '@/constants/project'

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
      dataIndex: 'name',
    },
    labeled: {
      title: title('dataset.analysis.column.labeled'),
      dataIndex: 'labeled',
      render: (_, record) => {
        const annoCounts = getAnnotations(record, type)
        const labeled = record.assetCount - annoCounts.negative
        return renderPop(humanize(labeled), labeled)
      },
      width: 80,
    },
    keywordsCount: {
      title: title('dataset.analysis.column.keywords.count'),
      dataIndex: 'keywords',
      render: (keywords) => keywords.length,
    },
    averageKeywordsCount: {
      title: title('dataset.analysis.column.keywords.count.average'),
      dataIndex: 'averageKeywordsCount',
      render: (_, record) => getAnnotations(record, type).average,
    },
    annotationsCount: {
      title: title('dataset.analysis.column.annotations.total'),
      dataIndex: 'average',
      render: (_, record) => getAnnotations(record, type).total,
    },
    averageAnnotationsCount: {
      title: title('dataset.analysis.column.annotations.average'),
      dataIndex: 'averageAnnotationsCount',
      render: (_, record) => getAnnotations(record, type).average,
    },
    annotationsAreaTotal: {
      title: title('dataset.analysis.column.annotations.total'),
      dataIndex: 'average',
      render: (_, record) => getAnnotations(record, type).total,
    },
    averageAnnotationsArea: {
      title: title('dataset.analysis.column.annotations.average'),
      dataIndex: 'averageAnnotationsCount',
      render: (_, record) => getAnnotations(record, type).average,
    },
    instanceCount: {
      title: title('dataset.analysis.column.annotations.total'),
      dataIndex: 'average',
      render: (_, record) => getAnnotations(record, type).total,
    },
    averageInstanceCount: {
      title: title('dataset.analysis.column.annotations.average'),
      dataIndex: 'averageAnnotationsCount',
      render: (_, record) => getAnnotations(record, type).average,
    },
    metrics: {
      title: title('dataset.analysis.column.overall'),
      dataIndex: 'metrics',
      render: (text, record) => {
        const total = record.assetCount
        const negative = getAnnotations(record, type).negative
        return renderPop(`${humanize(total - negative)}/${humanize(total)}`, `${total - negative}/${total}`)
      },
    },
  }
  return keys.map((key) => ({ ...columns[key], ellipsis: true, align: 'center' }))
}

function renderPop(label: ReactNode, content: ReactNode) {
  return (
    <Popover content={content}>
      <span>{label}</span>
    </Popover>
  )
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
const getCharts = (objectType?: YModels.ObjectType) => {
  const maps = {
    [ObjectType.ObjectDetection]: ['keywords', 'areaRatio'],
    [ObjectType.SemanticSegmentation]: [
      'keywords',
      // 标注面积统计
      'keywordArea',
    ],
    [ObjectType.InstanceSegmentation]: [
      'keywords',
      // 目标聚集度
      'crowdedness',
      // 实例面积分布
      'instanceArea',
      // 标注面积统计
      'keywordArea',
    ],
  }
  const assetCharts = ['assetHWRatio', 'assetQuality', 'assetArea']
  const keys = objectType ? maps[objectType] : assetCharts
  return keys.map((key) => charts[key])
}

export const getConfigByAnnotationType = (objectType: YModels.ObjectType, annotationType: AnnotationType) => {
  return {
    table: getTableColumns(objectType, annotationType),
    assetCharts: getCharts(),
    annotationCharts: getCharts(objectType),
  }
}
