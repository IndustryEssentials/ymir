import React, { useEffect, useState } from "react"
import { Button, Form, Row, Col, Table, Popover, Card, Radio } from "antd"
import { useParams } from "umi"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import { humanize } from "@/utils/number"

import Breadcrumbs from '@/components/common/breadcrumb'
import Panel from "@/components/form/panel"
import DatasetSelect from "@/components/form/datasetSelect"
import AnalysisChart from "./components/analysisChart"

import style from "./analysis.less"
import { CompareIcon } from "@/components/common/icons"

const options = [
  { value: 'gt' },
  { value: 'pred' }
]

function Analysis() {
  const [form] = Form.useForm()
  const { id: pid } = useParams()
  const [remoteSource, fetchSource] = useFetch('dataset/analysis')
  const [source, setSource] = useState([])
  const [datasets, setDatasets] = useState([])
  const [tableSource, setTableSource] = useState([])
  const [chartsData, setChartsData] = useState([])
  const [annotationsType, setAnnotationType] = useState(options[0].value)

  useEffect(() => {
    setTableSource(source)
    setAnalysisData(source)
  }, [source, annotationsType])

  useEffect(() => {
    setSource(remoteSource)
  }, [remoteSource])

  function setAnalysisData(datasets) {
    const chartsMap = [
      {
        label: 'dataset.analysis.title.asset_bytes',
        sourceField: 'assetBytes',
        totalField: 'assetCount',
        xUnit: 'MB',
        renderEachX: x => x.replace("MB", ""),
        color: ['#10BC5E', '#F2637B']
      },
      {
        label: 'dataset.analysis.title.asset_hw_ratio',
        sourceField: 'assetHWRatio',
        totalField: 'assetCount',
        color: ['#36CBCB', '#E8B900']
      },
      {
        label: 'dataset.analysis.title.asset_area',
        sourceField: 'assetArea',
        totalField: 'assetCount',
        xUnit: 'PX',
        renderEachX: x => `${x / 10000}W`,
        color: ['#36CBCB', '#F2637B'],
      },
      {
        label: 'dataset.analysis.title.asset_quality',
        sourceField: 'assetQuality',
        totalField: 'assetCount',
        color: ['#36CBCB', '#10BC5E'],
        isXUpperLimit: true,
      },
      {
        label: 'dataset.analysis.title.anno_area_ratio',
        sourceField: 'areaRatio',
        totalField: 'total',
        customOptions: {
          tooltipLable: 'dataset.analysis.bar.anno.tooltip',
        },
        color: ['#10BC5E', '#E8B900'],
        annoType: true,
        isXUpperLimit: true,
      },
      {
        label: 'dataset.analysis.title.keyword_ratio',
        sourceField: 'keywords',
        totalField: 'total',
        color: ['#2CBDE9', '#E8B900'],
        annoType: true,
        xType: 'attribute'
      },
    ]

    const chartsConfig = datasets ? chartsMap.map(chart => {
      const xData = chart.xType === 'attribute' ? getAttrXData(chart, datasets) : getXData(chart, datasets)
      const yData = chart.xType === 'attribute' ? getAttrYData(chart, datasets, xData) : getYData(chart, datasets)
      return {
        label: chart.label,
        customOptions: {
          ...chart.customOptions,
          xData,
          color: chart.color,
          xUnit: chart.xUnit,
          yData
        },
      }
    }) : []
    setChartsData(chartsConfig)
  }

  const getField = (item = {}, field, annoType) => {
    return annoType && item[annotationsType] ? item[annotationsType][field] : item[field]
  }

  function getXData({ sourceField, isXUpperLimit = false, annoType, renderEachX = x => x }, datasets) {
    const dataset = datasets.find(item => {
      const target = getField(item, sourceField, annoType)
      return target && target.length > 0
    }) || datasets[0]
    const field = getField(dataset, sourceField, annoType)
    const xData = field ? field.map(item => renderEachX(item.x)) : []
    const transferXData = xData.map((x, index) => {
      if (index === xData.length - 1) {
        return isXUpperLimit ? x : `[${x},+)`
      } else {
        return `[${x},${xData[index + 1]})`
      }
    })
    return transferXData
  }

  function getYData({ sourceField, annoType, totalField }, datasets) {
    const yData = datasets && datasets.map(dataset => {
      const total = getField(dataset, totalField, annoType)
      const name = `${dataset.name} ${dataset.versionName}`
      const field = getField(dataset, sourceField, annoType)
      return {
        name,
        value: field.map(item => total ? (item.y / total).toFixed(4) : 0),
        count: field.map(item => item.y)
      }
    })
    return yData
  }

  function getAttrXData({ sourceField, annoType }, datasets) {
    let xData = []
    datasets && datasets.forEach((dataset) => {
      const field = getField(dataset, sourceField, annoType)
      const datasetAttrs = Object.keys(field || {})
      xData = [...new Set([...xData, ...datasetAttrs])]
    })
    return xData
  }

  function getAttrYData({ sourceField, annoType, totalField }, datasets, xData) {
    const yData = datasets && datasets.map(dataset => {
      const total = getField(dataset, totalField, annoType)
      const name = `${dataset.name} ${dataset.versionName}`
      const attrObj = getField(dataset, sourceField, annoType)
      return {
        name,
        value: xData.map(key => total ? (attrObj[key] ? (attrObj[key] / total).toFixed(4) : 0) : 0),
        count: xData.map(key => attrObj[key] || 0)
      }
    })
    return yData
  }

  function datasetsChange(values, options) {
    setDatasets(options.map(option => option.dataset))
  }

  const onFinish = async (values) => {
    const params = {
      pid,
      datasets: values.datasets
    }
    fetchSource(params)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function retry() {
    setSource(null)
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  const columns = [
    {
      title: showTitle('dataset.analysis.column.name'),
      dataIndex: "name",
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
    },
    {
      title: showTitle('dataset.analysis.column.version'),
      dataIndex: "versionName",
      ellipsis: true,
      align: 'center',
      width: 80,
      className: style.colunmClass,
    },
    {
      title: showTitle('dataset.analysis.column.size'),
      dataIndex: "totalAssetMbytes",
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (num) => {
        return num && <span>{num}MB</span>
      },
    },
    {
      title: showTitle('dataset.analysis.column.box_count'),
      dataIndex: 'total',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (_, record) => {
        const num = getField(record, 'total', true)
        return renderPop(humanize(num), num)
      },
    },
    {
      title: showTitle('dataset.analysis.column.average_labels'),
      dataIndex: 'average',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (_, record) => getField(record, 'average', true),
    },
    {
      title: showTitle('dataset.analysis.column.overall'),
      dataIndex: 'metrics',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (text, record) => {
        const total = record.assetCount
        const negative = getField(record, 'negative', true)
        return renderPop(`${humanize(total - negative)}/${humanize(total)}`, `${total - negative}/${total}`)
      },
    },
  ]

  function renderPop(label, content = {}) {
    return <Popover content={content} >
      <span>{label}</span>
    </Popover>
  }

  async function validDatasetCount(rule, value) {
    const count = 5
    if (value?.length > count) {
      return Promise.reject(t('dataset.analysis.validator.dataset.count', { count }))
    } else {
      return Promise.resolve()
    }
  }

  const initialValues = {}

  return (
    <div className={style.wrapper}>
      <Breadcrumbs />
      <Card className={style.container} title={t('breadcrumbs.dataset.analysis')}>
        <Row gutter={20} className={style.dataContainer}>
          <Col span={18} className={style.rowData}>
            <div className={style.filters}>
              <Radio.Group
                value={annotationsType}
                options={options.map(opt => ({ ...opt, label: t(`annotation.${opt.value}`) }))}
                onChange={({ target: { value } }) => setAnnotationType(value)}
              ></Radio.Group>
            </div>
            <Table
              size="small"
              align='right'
              dataSource={tableSource}
              rowKey={(record) => record.name + record.versionName}
              rowClassName={style.rowClass}
              className={style.tableClass}
              columns={columns}
              pagination={false}
            />
            <Row gutter={[10, 20]}>
              {chartsData.map(chart => (
                <Col span={24} key={chart.label}>
                  <div className={style.echartTitle}>{t(chart.label)}</div>
                  <AnalysisChart customOptions={chart.customOptions} height={300} />
                </Col>
              ))}
            </Row>
          </Col>
          <Col span={6} className='rightForm'>
            <div className='mask' hidden={!source}>
              <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}>
                <CompareIcon /> {t('dataset.analysis.btn.retry')}
              </Button>
            </div>
            <Panel label={t('dataset.analysis.param.title')} style={{ marginTop: -10 }} toogleVisible={false}>
              <Form
                className={style.analysisForm}
                form={form}
                layout='vertical'
                name='labelForm'
                initialValues={initialValues}
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                labelAlign='left'
                colon={false}
              >
                <Form.Item
                  label={t('dataset.analysis.column.name')}
                  name='datasets'
                  rules={[
                    { required: true },
                    { validator: validDatasetCount }
                  ]}>
                  <DatasetSelect pid={pid} mode='multiple' onChange={datasetsChange} />
                </Form.Item>
                <Form.Item name='submitBtn'>
                  <div style={{ textAlign: 'center' }}>
                    <Button type="primary" size="large" htmlType="submit">
                      <CompareIcon /> {t('dataset.analysis.btn.start')}
                    </Button>
                  </div>
                </Form.Item>
              </Form>
            </Panel>
          </Col>
        </Row>

      </Card>
    </div>
  )
}

export default Analysis
