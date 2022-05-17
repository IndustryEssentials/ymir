import React, { useCallback, useEffect, useState } from "react"
import { connect } from "dva"
import { Card, Button, Form, Row, Col, Space, Table, Slider, } from "antd"
import s from "./index.less"
import commonStyles from "../common.less"
import { useHistory, useParams, Link } from "umi"

import t from "@/utils/t"
import { string2Array } from "@/utils/string"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber, toFixed } from "@/utils/number"
import Panel from "@/components/form/panel"
import DatasetSelect from "@/components/form/datasetSelect"
import { CompareIcon } from "@/components/common/icons"
import useDynamicRender from "@/hooks/useDynamicRender"
import KeywordSelect from "./components/keywordSelect"
import useBatchModels from "../../../hooks/useBatchModels"

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
  const [keywords, setKeywords] = useState([])
  const [source, setSource] = useState(null)
  const [tableSource, setTableSource] = useState([])
  const [form] = Form.useForm()
  const [apRender, setSelectedKeyword] = useDynamicRender()
  const [models, getModels] = useBatchModels()

  const filterDatasets = useCallback((dss) => {
    return filterSameAssets(innerGroup(dss)).filter(ds => ds.id !== gt?.id)
  }, [gt])

  const filterGT = useCallback((dss) => {
    return filterSameAssets(innerGroup(dss)).filter(ds => !datasets.map(({ id }) => id).includes(ds.id))
  }, [datasets])

  useEffect(() => {
    setTableSource(generateTableSource(iou))
  }, [iou, source])

  useEffect(() => {
    !source && setKeywords([])
  }, [source])

  const onFinish = async (values) => {
    const params = {
      ...values,
      projectId: pid,
      name: 'task_eveluate_' + randomNumber(),
    }
    const result = await func.compare(params)
    if (result) {
      setSource(result)
      const list = gt.keywords || []
      setKeywords(list)
      fetchModels()
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function datasetsChange(values, options) {
    setDatasets(options.map(option => option.dataset))
  }

  function gtChange(value, option = {}) {
    setGT(option?.dataset)
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
      model: dataset.task?.parameters?.model_id,
    })
    return source ? [getInfo(gt), ...datasets.map((dataset, index) => {
      const datasetSource = source[dataset.id] || {}
      const iouMetrics = datasetSource.iou_evaluations || {}
      const metrics = iouMetrics[iou] || {}
      return {
        ...getInfo(dataset),
        map: datasetSource.iou_averaged_evaluation,
        metrics,
        dataset,
      }
    })] : []
  }

  function retry() {
    setSource(null)
  }

  function getModelsName(id) {
    const model  = models.find(md => md.id === id)
    return model ? `${model.name} ${model.versionName}` : null
  }

  function fetchModels () {
    if (datasets.length) {
      const ids = datasets.map(({ task: { parameters: { model_id } } }) => model_id).filter(item => item)
      getModels(ids)
    }
  }

  const columns = [
    {
      title: t("dataset.column.name"),
      dataIndex: "name",
      render: (name, { id }) => {
        const extra = id === gt.id ? <span className={s.extra}>Ground Truth</span> : null
        return <>{name} {extra}</>
      },
      ellipsis: {
        showTitle: true,
      },
    },
    {
      title: t("dataset.column.model"),
      dataIndex: "model",
      render: id => <Link to={`/home/project/${pid}/model/${id}`}>{getModelsName(id)}</Link>,
      ellipsis: {
        showTitle: true,
      },
    },
    {
      title: t("dataset.column.map"),
      dataIndex: "map",
      render: apRender,
    },
    {
      title: 'AP',
      dataIndex: 'metrics',
      render: apRender,
      ellipsis: {
        showTitle: true,
      },
    },
  ]

  function renderTitle() {
    return (
      <Row>
        <Col flex={1}>{t('breadcrumbs.dataset.compare')}</Col>
        <Col><Button type='link' onClick={() => history.goBack()}>{t('common.back')}&gt;</Button></Col>
      </Row>
    )
  }

  const initialValues = {
    datasets: did,
    confidence,
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={renderTitle()}>
        <Row gutter={20}>
          <Col span={18} style={{ border: '1px solid #ccc' }}>
            <Space className={s.info} size={20}>
              <span>{t('dataset.compare.form.confidence')}: {source ? confidence : 0}</span>
              <span>IoU:</span>
              <span>
                <Slider style={{ width: 300 }} min={0.5} max={0.95}
                  tooltipVisible marks={{ 0.5: '0.5', 0.95: '0.95' }}
                  step={0.05} value={iou} onChange={value => setIou(value)} />
              </span>
              <span><KeywordSelect keywords={keywords} onChange={selected => setSelectedKeyword(selected)} /></span>
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
            <Panel label={t('breadcrumbs.dataset.compare')} style={{ marginTop: -10 }} toogleVisible={false}>
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
                  <DatasetSelect pid={pid} mode='multiple' filterOption={false} filters={filterDatasets} onChange={datasetsChange} />
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
                  <Slider min={0} max={0.9} step={0.1} value={confidence} tooltipVisible marks={{ 0: '0', 0.5: '0.5', 0.9: '0.9' }} onChange={setConfidence} />
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
