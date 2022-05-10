import React, { useCallback, useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Input, Card, Button, Form, Row, Col, Checkbox, ConfigProvider, Space, Radio, Tag, InputNumber, Table, Dropdown, Menu, Progress, Slider, } from "antd"
import s from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"
import { useHistory, useParams, Link, useLocation } from "umi"

import t from "@/utils/t"
import Uploader from "@/components/form/uploader"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import Panel from "@/components/form/panel"
import DatasetSelect from "../../../components/form/datasetSelect"
import { ArrowDownIcon, CompareIcon } from "../../../components/common/icons"

function string2Array(str) {
  return str.split(',').map(i => +i)
}

const useDynamicColumn = () => {
  const [options, setOptions] = useState([])
  const [selected, setSelected] = useState(null)
  const change = ({ key }) => setSelected(key)
  useEffect(() => {
    setSelected(options.length ? options[0] : '')
  }, [options])
  const menus = <Menu items={options.map(option => ({ key: option, label: option }))} onClick={change} />
  const title = <Dropdown overlay={menus}>
    <Space>
      {selected}
      <ArrowDownIcon />
    </Space>
  </Dropdown>
  const column = {
    title,
    dataIndex: "metrics",
    render: (metrics = []) => {
      const target = metrics.find(met => met.keyword === selected)
      return target?.ap
    },
    ellipsis: {
      showTitle: true,
    },
  }
  return [column, setOptions]
}

function Compare({ ...func }) {
  const history = useHistory()
  const pageParams = useParams()
  const pid = +pageParams.id
  const gid = +pageParams.gid
  const did = string2Array(pageParams.ids)
  const [datasets, setDatasets] = useState([])
  const [gt, setGT] = useState({})
  const [iou, setIou] = useState(0.5)
  const [confidence, setConfidence] = useState(0.3)
  const [source, setSource] = useState(null)
  const [tableSource, setTableSource] = useState([])
  const [form] = Form.useForm()
  const [dynamicColumn, setDynamicColumn] = useDynamicColumn()

  const filterDatasets = useCallback((dss) => {
    return filterSameAssets(innerGroup(dss)).filter(ds => ds.id !== gt.id)
  }, [gt])

  const filterGT = useCallback((dss) => {
    return filterSameAssets(innerGroup(dss)).filter(ds => !datasets.map(({ id }) => id).includes(ds.id))
  }, [datasets])

  useEffect(() => {
    setTableSource(generateTableSource(iou))
  }, [iou, source])

  useEffect(() => {
    const list = gt.keywords || []
    setDynamicColumn(tableSource.length ? list : [])
  }, [tableSource])

  const onFinish = async (values) => {
    const params = {
      ...values,
      projectId: pid,
      name: 'task_eveluate_' + randomNumber(),
    }
    const result = await func.compare(params)
    console.log('compare result:', result, datasets)
    if (result) {
      setSource(result)
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function datasetsChange(values, options) {
    setDatasets(options.map(option => option.dataset))
  }

  function gtChange(value, option) {
    setGT(option.dataset)
  }

  function innerGroup(datasets) {
    return datasets.filter(ds => ds.groupId === gid)
  }

  function filterSameAssets(datasets = []) {
    if (!datasets.length) {
      return datasets
    }
    const target = datasets.find(({ id }) => id === did[0])
    const count = target.assetCount
    return datasets.filter(({ assetCount }) => count === assetCount)
  }

  function generateTableSource(iou = 0) {
    const getInfo = (dataset) => ({
      id: dataset.id,
      name: `${dataset.name} ${dataset.versionName}`,
      model: dataset.task?.parameters?.model_name,
      modelId: dataset.task?.parameters?.model_id,
    })
    return source ? [getInfo(gt), ...datasets.map((dataset, index) => {
      const datasetSource = source[dataset.id]
      const metrics = datasetSource.metrics.filter(m => m.iou_threshold === iou)
      return {
        ...getInfo(dataset),
        map: datasetSource.map,
        metrics,
        dataset,
      }
    })] : []
  }

  function retry() {
    setSource(null)
  }

  const columns = [
    {
      title: t("dataset.column.name"),
      dataIndex: "name",
      render: (name, { id }) => {
        const extra = id === gt.id ? <span className={s.extra}>Ground Truth</span> : null
        return <>{ name } { extra}</>
      },
      ellipsis: {
        showTitle: true,
      },
    },
    {
      title: t("dataset.column.model"),
      dataIndex: "model",
      render: (name, { modelId }) => <Link to={`/home/project/${pid}/model/${modelId}`}>{name}</Link>,
      ellipsis: {
        showTitle: true,
      },
    },
    {
      title: t("dataset.column.map"),
      dataIndex: "map",
    },
    dynamicColumn,
  ]

  const initialValues = {
    datasets: did,
    confidence,
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.dataset.compare')}>
        <Row gutter={20}>
          <Col span={18} style={{ border: '1px solid #ccc' }}>
            <Space className={s.info}>
              <span>{t('dataset.compare.form.confidence')}: {source ? confidence : 0}</span>
              <span>IoU:</span>
              <span>
                <Slider style={{ width: 300 }} min={0.5} max={0.95} tooltipVisible marks={{ 0.5: '0.5', 0.95: '0.95' }} step={0.05} value={iou} onChange={value => setIou(value)} />
              </span>
            </Space>
            <Table
              dataSource={tableSource}
              rowKey={(record) => record.id}
              rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
              columns={columns}
              pagination={false}
            />
          </Col>
          <Col span={6} className={s.formContainer}>
            <div className={s.mask} hidden={!source}>
              <Button style={{ marginBottom: 24 }} size='large' type="primary" onClick={() => retry()}><CompareIcon /> {t('dataset.compare.restart')}</Button>
            </div>
            <Panel label={t('breadcrumbs.dataset.compare')} style={{ marginTop: -10 }} visible={true}>
              <Form
                className={s.form}
                form={form}
                layout={'vertical'}
                name='labelForm'
                initialValues={initialValues}
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                labelAlign={'left'}
                colon={false}
              >
                <Form.Item
                  label={t('dataset.compare.form.datasets')}
                  name='datasets'
                  rules={[
                    { required: true }
                  ]}
                >
                  <DatasetSelect pid={pid} mode='multiple' filters={filterDatasets} onChange={datasetsChange} />
                </Form.Item>
                <Form.Item
                  label={t('dataset.compare.form.gt')}
                  name='gt'
                  rules={[
                    { required: true }
                  ]}
                >
                  <DatasetSelect pid={pid} filters={filterGT} onChange={gtChange} />
                </Form.Item>
                <Form.Item label={t('dataset.compare.form.confidence')} name='confidence'>
                  <Slider min={0} max={1} step={0.1} value={confidence} tooltipVisible marks={{ 0: '0', 0.5: '0.5', 1: '1' }} onChange={setConfidence} />
                </Form.Item>
                <Form.Item name='submitBtn'>
                  <div style={{ textAlign: 'center' }}>
                  <Button type="primary" size="large" htmlType="submit">
                    <CompareIcon /> {t('common.action.compare')}
                  </Button>
                  </div>
                </Form.Item>
              </Form>
            </Panel>
          </Col>
        </Row>
      </Card>
    </div >
  )
}

const dis = (dispatch) => {
  return {
    getDataset(id, force) {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
      })
    },
    compare(payload) {
      return dispatch({
        type: "dataset/compare",
        payload,
      })
    },
  }
}

const stat = (state) => {
  return {
    // allDatasets: state.dataset.allDatasets,
  }
}

export default connect(stat, dis)(Compare)
