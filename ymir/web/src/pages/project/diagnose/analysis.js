import React, { useEffect, useState } from "react"
import { Button, Form, Row, Col, Table, Popover } from "antd"
import { connect } from "dva"
import s from "./index.less"
import style from "./analysis.less"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import { humanize } from "@/utils/number"
import Panel from "@/components/form/panel"
import DatasetSelect from "@/components/form/datasetSelect"
import { CompareIcon } from "@/components/common/icons"
import AnalysisChart from "./components/analysisChart"

function Analysis({pid, project, ...func}) {
  const [form] = Form.useForm()
  const [remoteSource, fetchSource] = useFetch('dataset/analysis')
  const [source, setSource] = useState([])
  const [datasets, setDatasets] = useState([])
  const [tableSource, setTableSource] = useState([])
  const [chartsData, setChartsData] = useState([])

  useEffect(() => {
    setTableSource(source);
    setAnalysisData(source);
  }, [source])

  useEffect(() => {
    setSource(remoteSource);
  }, [remoteSource])
  
  function setAnalysisData(datasets) {
    const chartsMap= [
      {
        label: 'model.diagnose.analysis.title.asset_bytes',
        sourceField: 'assetBytes',
        totalField: 'assetCount',
        xUnit: 'MB',
        renderEachX: x => x.replace("MB",""),
        color: ['#10BC5E', '#F2637B']
      },
      {
        label: 'model.diagnose.analysis.title.asset_hw_ratio',
        sourceField: 'assetHWRatio',
        totalField: 'assetCount',
        color: ['#36CBCB', '#E8B900']
      },
      {
        label: 'model.diagnose.analysis.title.asset_area',
        sourceField: 'assetArea',
        totalField: 'assetCount',
        xUnit: 'PX',
        renderEachX: x => `${x/10000}W`,
        color: ['#36CBCB', '#F2637B'],
      },
      {
        label: 'model.diagnose.analysis.title.asset_quality',
        sourceField: 'assetQuality',
        totalField: 'assetCount',
        color: ['#36CBCB', '#10BC5E'],
        isXUpperLimit: true,
      },
      {
        label: 'model.diagnose.analysis.title.anno_area_ratio',
        sourceField: 'annoAreaRatio',
        totalField: 'annosCnt',
        customOptions: {
          tooltipLable: 'model.diagnose.analysis.bar.anno.tooltip',
        },
        color: ['#10BC5E', '#E8B900'],
        isXUpperLimit: true,
      },
      {
        label: 'model.diagnose.analysis.title.keyword_ratio',
        sourceField: 'classNamesCount',
        totalField: 'assetCount',
        color: ['#2CBDE9', '#E8B900'],
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
    setChartsData(chartsConfig);
  }

  function getXData({sourceField, isXUpperLimit = false, renderEachX = x => x}, datasets) {
    const dataset = datasets.find(item => item[sourceField] && item[sourceField].length > 0) || datasets[0]
    const xData = dataset && dataset[sourceField] ? dataset[sourceField].map(item => renderEachX(item.x)) : [];
    const transferXData = xData.map((x,index) => {
      if (index === xData.length - 1) {
        return isXUpperLimit ? x : `[${x},+)`
      } else {
        return `[${x},${xData[index + 1]})`
      }
    })
    return transferXData;
  }

  function getYData({sourceField, totalField}, datasets) {
    const yData = datasets && datasets.map(dataset => {
      const total = dataset[totalField];
      const name = `${dataset.name} ${dataset.versionName}`
      return {
        name,
        value: dataset[sourceField].map(item => total ? (item.y / total).toFixed(4) : 0),
        count: dataset[sourceField].map(item => item.y)
      }
    })
    return yData;
  }

  function getAttrXData({sourceField}, datasets) {
    let xData = []
    datasets && datasets.forEach((dataset) => {
      const datasetAttrs = Object.keys(dataset[sourceField]|| {});
      xData = [...new Set([...xData, ...datasetAttrs])];
    })
    return xData;
  }

  function getAttrYData({sourceField, totalField}, datasets, xData) {
    const yData = datasets && datasets.map(dataset => {
      const total = dataset[totalField];
      const name = `${dataset.name} ${dataset.versionName}`
      const attrObj = dataset[sourceField];
      return {
        name,
        value: xData.map(key => total ? (attrObj[key] ? (attrObj[key] / total).toFixed(4) : 0) : 0),
        count: xData.map(key => attrObj[key] || 0)
      }
    })
    return yData;
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
      title: showTitle('model.diagnose.analysis.column.name'),
      dataIndex: "name",
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
    },
    {
      title: showTitle('model.diagnose.analysis.column.version'),
      dataIndex: "versionName",
      ellipsis: true,
      align: 'center',
      width: 80,
      className: style.colunmClass,
    },
    {
      title: showTitle('model.diagnose.analysis.column.size'),
      dataIndex: "totalAssetMbytes",
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (num) => {
        return num && <span>{num}MB</span>;
      },
    },
    {
      title: showTitle('model.diagnose.analysis.column.box_count'),
      dataIndex: 'annosCnt',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (num) => renderPop(humanize(num), num),
    },
    {
      title: showTitle('model.diagnose.analysis.column.average_labels'),
      dataIndex: 'aveAnnosCnt',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
    },
    {
      title: showTitle('model.diagnose.analysis.column.overall'),
      dataIndex: 'metrics',
      ellipsis: true,
      align: 'center',
      className: style.colunmClass,
      render: (text, record) => renderPop(`${humanize(record.positiveAssetCnt)}/${humanize(record.assetCount)}`, `${record.positiveAssetCnt}/${record.assetCount}`),
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
      return Promise.reject(t('model.diagnose.analysis.validator.dataset.count', {count}))
    } else {
      return Promise.resolve()
    }
  }

  const initialValues = {}
 
  return (
    <div className={s.wrapper}>
      <Row gutter={20} className={style.dataContainer}>
        <Col span={18} className={style.rowData}>
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
                <AnalysisChart customOptions={chart.customOptions} height={300}/>
              </Col>
            ))}
          </Row>
        </Col>
        <Col span={6} className={s.formContainer}>
          <div className={s.mask} hidden={!source}>
            <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}>
              <CompareIcon /> {t('model.diagnose.analysis.btn.retry')}
            </Button>
          </div>
          <Panel label={t('model.diagnose.analysis.param.title')} style={{ marginTop: -10 }} toogleVisible={false}>
            <Form
              className={s.form}
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
                label={t('model.diagnose.analysis.column.name')}
                name='datasets'
                rules={[
                  { required: true},
                  { validator: validDatasetCount}
                ]}>
                <DatasetSelect pid={pid} mode='multiple' onChange={datasetsChange} />
              </Form.Item>
              <Form.Item name='submitBtn'>
                <div style={{ textAlign: 'center' }}>
                  <Button type="primary" size="large" htmlType="submit">
                    <CompareIcon /> {t('model.diagnose.analysis.btn.start_diagnose')}
                  </Button>
                </div>
              </Form.Item>
            </Form>
          </Panel>
        </Col>
      </Row>
    </div >
  )
}

export default Analysis
