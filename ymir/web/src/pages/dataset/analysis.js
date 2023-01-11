import React, { useEffect, useState } from 'react'
import { Button, Form, Row, Col, Table, Popover, Card, Radio } from 'antd'
import { useParams } from 'umi'

import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import useRequest from '@/hooks/useRequest'

import Breadcrumbs from '@/components/common/breadcrumb'
import Panel from '@/components/form/panel'
import DatasetSelect from '@/components/form/datasetSelect'
import AnalysisChart from './components/analysisChart'
import { getConfigByAnnotationType } from './components/AnalysisHelper'

import style from './analysis.less'
import { CompareIcon } from '@/components/common/Icons'

const options = ['gt', 'pred']

const getVersionName = ({ name, versionName }) => `${name} ${versionName}`
function Analysis() {
  const [form] = Form.useForm()
  const { id: pid } = useParams()
  const [remoteSource, fetchSource] = useFetch('dataset/analysis')
  const [source, setSource] = useState([])
  const [assetCharts, setAssetCharts] = useState([])
  const [annotationCharts, setAnnotationCharts] = useState([])
  const [annotationsType, setAnnotationType] = useState(options[0])
  const [{ tableColumns, assetChartConfig, annotationChartConfig }, setConfig] = useState({
    tableColumns: [],
    assetChartConfig: [],
    annotationChartConfig: [],
  })
  const { data: project, run: getProject } = useRequest('project/getProject', {
    loading: false,
  })

  useEffect(() => {
    getProject({ id: pid })
  }, [])

  useEffect(() => {
    project && setConfig(getConfigByAnnotationType(project.type, annotationsType))
  }, [project, annotationsType])

  useEffect(() => {
    const charts = generateCharts(assetChartConfig, source)
    setAssetCharts(charts)
  }, [assetChartConfig, source])

  useEffect(() => {
    const charts = generateCharts(annotationChartConfig, source)
    setAnnotationCharts(charts)
  }, [annotationChartConfig, source])

  useEffect(() => {
    setSource(remoteSource || [])
  }, [remoteSource])

  function generateCharts(configs = [], datasets = []) {
    return datasets.length ? configs.map((config) => {
      const xData = config.xType === 'attribute' ? getAttrXData(config, datasets) : getXData(config, datasets)
      const yData = config.xType === 'attribute' ? getAttrYData(config, datasets, xData) : getYData(config, datasets)
      return {
        label: config.label,
        customOptions: {
          ...config.customOptions,
          xData,
          color: config.color,
          xUnit: config.xUnit,
          yData,
        },
      }
    }) : []
  }

  function getXData(config, datasets) {
    const { sourceField, isXUpperLimit = false, getSource, renderEachX = (x) => x } = config
    const dataset =
      datasets.find((item) => {
        const target = getSource(item)
        return target && target.length > 0
      }) || datasets[0]
    const field = getSource(dataset)[sourceField]
    const xData = field ? field.map((item) => renderEachX(item.x)) : []
    const transferXData = xData.map((x, index) => {
      if (index === xData.length - 1) {
        return isXUpperLimit ? x : `[${x},+)`
      } else {
        return `[${x},${xData[index + 1]})`
      }
    })
    return transferXData
  }

  function getYData({ getSource, sourceField, totalField }, datasets) {
    const yData =
      datasets &&
      datasets.map((dataset) => {
        const data = getSource(dataset)
        const total = data[totalField] || dataset[totalField]
        const name = getVersionName(dataset)
        const field = data[sourceField]
        return {
          name,
          value: field.map((item) => (total ? item.y / total : 0)),
          count: field.map((item) => item.y),
        }
      })
    return yData
  }

  function getAttrXData({ sourceField, getSource }, datasets) {
    let xData = []
    datasets &&
      datasets.forEach((dataset) => {
        const field = getSource(dataset)[sourceField]
        const datasetAttrs = Object.keys(field || {})
        xData = [...new Set([...xData, ...datasetAttrs])]
      })
    return xData
  }

  function getAttrYData({ getSource, sourceField, totalField }, datasets, xData) {
    const yData =
      datasets &&
      datasets.map((dataset) => {
        const data = getSource(dataset)
        const total = data[totalField] || dataset[totalField]
        const name = getVersionName(dataset)
        const attrObj = data[sourceField]
        return {
          name,
          value: xData.map((key) => (total ? (attrObj[key] ? attrObj[key] / total : 0) : 0)),
          count: xData.map((key) => attrObj[key] || 0),
        }
      })
    return yData
  }

  const onFinish = async (values) => {
    const params = {
      pid,
      datasets: values.datasets,
    }
    fetchSource(params)
  }

  function onFinishFailed(errorInfo) {
    console.log('Failed:', errorInfo)
  }

  function retry() {
    setSource([])
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

  const chartsRender = (label, charts = []) =>
    charts.length ? (
      <>
        <h3>{t(label)}</h3>
        <Row gutter={[10, 20]}>
          {charts.map((chart) => (
            <Col span={24} key={chart.label}>
              <div className={style.echartTitle}>{t(chart.label)}</div>
              <AnalysisChart customOptions={chart.customOptions} height={300} />
            </Col>
          ))}
        </Row>
      </>
    ) : null

  return (
    <div className={style.wrapper}>
      <Breadcrumbs />
      <Card className={style.container} title={t('breadcrumbs.dataset.analysis')}>
        <Row gutter={20} className={style.dataContainer}>
          <Col span={18} className={style.rowData}>
            <div className={style.filters}>
              <Radio.Group
                value={annotationsType}
                options={options.map((value) => ({ value, label: t(`annotation.${value}`) }))}
                onChange={({ target: { value } }) => setAnnotationType(value)}
              ></Radio.Group>
            </div>
            <Table
              size="small"
              align="right"
              dataSource={source}
              rowKey={(record) => getVersionName(record)}
              rowClassName={style.rowClass}
              className={style.tableClass}
              columns={tableColumns}
              pagination={false}
            />
            {chartsRender('dataset.analysis.annotations.metrics', annotationCharts)}
            {chartsRender('dataset.analysis.assets.metrics', assetCharts)}
          </Col>
          <Col span={6} className="rightForm">
            <div className={style.formContainer}>
              <div className="mask" hidden={!source.length}>
                <Button style={{ marginBottom: 24 }} size="large" type="primary" onClick={() => retry()}>
                  <CompareIcon /> {t('dataset.analysis.btn.retry')}
                </Button>
              </div>
              <Panel label={t('dataset.analysis.param.title')} style={{ marginTop: -10 }} toogleVisible={false}>
                <Form
                  className={style.analysisForm}
                  form={form}
                  layout="vertical"
                  name="labelForm"
                  initialValues={initialValues}
                  onFinish={onFinish}
                  onFinishFailed={onFinishFailed}
                  labelAlign="left"
                  colon={false}
                >
                  <Form.Item label={t('dataset.analysis.column.name')} name="datasets" rules={[{ required: true }, { validator: validDatasetCount }]}>
                    <DatasetSelect pid={pid} mode="multiple" />
                  </Form.Item>
                  <Form.Item name="submitBtn">
                    <div style={{ textAlign: 'center' }}>
                      <Button type="primary" size="large" htmlType="submit">
                        <CompareIcon /> {t('dataset.analysis.btn.start')}
                      </Button>
                    </div>
                  </Form.Item>
                </Form>
              </Panel>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

export default Analysis
