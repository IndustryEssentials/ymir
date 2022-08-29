import React, { useCallback, useEffect, useState } from "react"
import { Card, Button, Form, Row, Col, Radio, Slider, Select, InputNumber, Checkbox, Space, } from "antd"
import s from "./index.less"

import t from "@/utils/t"
import useFetch from "@/hooks/useFetch"
import Panel from "@/components/form/panel"
import InferResultSelect from "@/components/form/inferResultSelect"
import MapView from "./components/mapView"
import CurveView from "./components/curveView"
import PView from "./components/prView"
import View from './components/view'

import { CompareIcon } from "@/components/common/icons"
import DefaultStages from "./components/defaultStages"

const metricsTabs = [
  { value: 'map', component: MapView, },
  { value: 'curve', component: CurveView, },
  { value: 'rp', component: PView, },
  { value: 'pr', component: PView, },
]

const xAxisOptions = [
  { key: 'dataset', value: 0 },
  { key: 'keyword', value: 1 },
]

const kwTypes = [{ label: 'keyword.add.name.label', value: 0 }, { label: 'keyword.ck.label', value: 1 }]

function Matrics({ pid, project }) {
  const [form] = Form.useForm()
  const [inferTasks, setInferTasks] = useState([])
  const [selectedModels, setSelectedModels] = useState([])
  const [selectedDatasets, setSelectedDatasets] = useState([])
  const [iou, setIou] = useState(0.5)
  const [everageIou, setEverageIou] = useState(false)
  const [confidence, setConfidence] = useState(0.3)
  const [selectedMetric, setSelectedMetric] = useState(metricsTabs[0].value)
  const [prRate, setPrRate] = useState([0.8, 0.95])
  const [keywords, setKeywords] = useState([])
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [ck, setCK] = useState([])
  const [kwType, setKwType] = useState(0)
  const [kws, setKws] = useState([])
  const [xAxis, setXAsix] = useState(xAxisOptions[0].value)
  const [remoteData, fetchDiagnosis] = useFetch('dataset/evaluate')
  const [diagnosis, setDiagnosis] = useState(null)
  const [diagnosing, setDiagnosing] = useState(false)
  const [kwFilter, setKwFilter] = useState({
    kwType: 0,
    keywords: [],
  })
  const [ckDatasets, getCKDatasets] = useFetch('dataset/analysis', [])
  const [cks, setCKs] = useState([])

  useEffect(() => {
    setDiagnosis(remoteData)
  }, [remoteData])

  useEffect(() => {
    if (diagnosing) {
      const kws = [...new Set(selectedModels.map(({ keywords }) => keywords).flat())]
      setKeywords(kws)
    } else {
      setKeywords([])
    }
  }, [selectedModels, diagnosing])

  useEffect(() => {
    // calculate ck
    const cks = diagnosis ?
      Object.values(diagnosis).map(({ iou_averaged_evaluation }) =>
        Object.keys(iou_averaged_evaluation.ck_evaluations)).flat() :
      []

    setCK([...new Set(cks)])
  }, [diagnosis])

  useEffect(() => {
    const kws = !kwType ? keywords : ck
    setKws(kws)
  }, [kwType, keywords, ck])

  useEffect(() => {
    setSelectedKeywords(kwType ? undefined : [])
  }, [kwType])

  useEffect(() => {
    setDiagnosing(!!diagnosis)
    setSelectedKeywords([])
  }, [diagnosis])

  useEffect(() => {
    setKwFilter({
      keywords: selectedKeywords?.length ? selectedKeywords : (kwType ? null : keywords),
      kwType,
    })
  }, [selectedKeywords, keywords])

  useEffect(() => {
    if (selectedDatasets.length) {
      getCKDatasets({ ids: selectedDatasets.map(({ id }) => id) })
    }
  }, [selectedDatasets])

  useEffect(() => {
    const allCks = ckDatasets.map(({ cks }) => cks).flat()
    allCks.filter(({ keyword }) => {
      const same = allCks.filter(k => k === keyword)
      return same.length === ckDatasets.length
    })
    setCKs(cks)
  }, [ckDatasets])

  const onFinish = async (values) => {
    const inferDataset = inferTasks.map(({ result }) => result)
    const params = {
      ...values,
      projectId: pid,
      everageIou,
      datasets: inferDataset,
    }
    fetchDiagnosis(params)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  function inferResultChange({ tasks, models, datasets }) {
    setInferTasks(tasks.map(
      ({ config, configName, parameters: { dataset_id, model_id, model_stage_id }, result_dataset: { id } }) =>
        ({ config, configName, testing: dataset_id, model: model_id, stage: model_stage_id, result: id })))
    setSelectedDatasets(datasets)
    setSelectedModels(models)
  }

  function metricsChange({ target: { value } }) {
    setSelectedMetric(value)
  }

  function prRateChange(value) {
    console.log('value:', value)
    setPrRate(value)
  }

  function xAxisChange({ target: { value } }) {
    setXAsix(value)
  }

  function kwChange(values) {
    setSelectedKeywords(values)
  }

  function retry() {
    setDiagnosis(null)
    setDiagnosing(false)
  }

  function renderView() {
    const panel = metricsTabs.find(({ value }) => selectedMetric === value)
    const Viewer = View(panel.component)
    return <Viewer
      tasks={inferTasks}
      models={selectedModels}
      datasets={selectedDatasets}
      data={diagnosis}
      prType={selectedMetric === 'pr' ? 0 : 1}
      prRate={prRate}
      xType={xAxis}
      kw={kwFilter}
    />
  }

  const renderFilterPanel = () => <div className={s.filterPanel}>
    <Space size={20} style={{ marginBottom: 10 }}>
      <span>{t('model.diagnose.metrics.view.label')}</span>
      <Radio.Group
        defaultValue={metricsTabs[0].value}
        options={metricsTabs.map(item => ({ ...item, label: t(`model.diagnose.medtric.tabs.${item.value}`) }))}
        onChange={metricsChange}
      />
      <div hidden={![metricsTabs[2].value, metricsTabs[3].value].includes(selectedMetric)}>
        <Slider className={s.prRate} style={{ width: 200 }} min={0} max={1}
          value={prRate}
          range={true}
          onChange={prRateChange}
          step={0.05} />
      </div>
    </Space>
    <Row gutter={20}>
      <Col>
        <Select value={kwType} options={kwTypes.map(({ label, value }) => ({ value, label: t(label) }))} onChange={setKwType}></Select>
      </Col>
      <Col flex={1}>
        <Select style={{ width: '100%' }} mode={kwType ? 'single' : "multiple"}
          value={selectedKeywords}
          options={kws.map(kw => ({ label: kw, value: kw }))}
          placeholder={t(kwType ? 'model.diagnose.metrics.ck.placeholder' : 'model.diagnose.metrics.keyword.placeholder')}
          showArrow onChange={kwChange}></Select>
      </Col>
      <Col>
        <Space size={20}>
          <span>{t('model.diagnose.metrics.dimension.label')}</span>
          <Radio.Group defaultValue={xAxisOptions[0].value} options={xAxisOptions.map(({ key, value }) => ({ value, label: t(`model.diagnose.metrics.x.${key}`) }))} onChange={xAxisChange} />
        </Space>
      </Col>
    </Row>
  </div>

  const renderViewPanel = () => <div className={s.metricsPanel}>{renderView()}</div>

  const renderIouTitle = <Space>
    <span>{t('model.diagnose.form.iou')}</span>
    <Checkbox checked={everageIou} onChange={({ target: { checked } }) => setEverageIou(checked)}>Average IOU</Checkbox>
  </Space>

  // todo form initial values
  const initialValues = {
    iou,
    confidence,
  }
  return (
    <div className={s.wrapper}>
      <Row className={s.view} gutter={20}>
        <Col className={s.viewPanel} span={18}>
          {renderFilterPanel()}
          {renderViewPanel()}
        </Col>
        <Col span={6}>
          <div className={s.formContainer}>

            <div className={s.mask} hidden={!diagnosing}>
              <Button style={{ marginBottom: 10 }} size='large' type="primary" onClick={() => retry()}><CompareIcon /> {t('model.diagnose.metrics.btn.retry')}</Button>
            </div>
            <Panel label={'Metrics'} style={{ marginTop: -10 }} toogleVisible={false}>
              <Form
                className={s.form}
                form={form}
                layout='vertical'
                initialValues={initialValues}
                onFinish={onFinish}
                onFinishFailed={onFinishFailed}
                labelAlign='left'
                colon={false}
              >
                <InferResultSelect form={form} pid={pid} onChange={inferResultChange} />
                <Form.Item label={t('model.diagnose.form.confidence')} name='confidence'>
                  <InputNumber step={0.0005} min={0.0005} max={0.9995} />
                </Form.Item>
                <Form.Item label={'cks'}>
                  <Select options={cks.map(({ keyword }) => ({ value: keyword, label: keyword }))}></Select>
                </Form.Item>
                <Form.Item label={renderIouTitle} name='iou'>
                  <Slider style={{ display: !everageIou ? 'block' : 'none' }} min={0.25} max={0.95} step={0.05} marks={{ 0.25: '0.25', 0.5: '0.5', 0.95: '0.95' }} onChange={setIou} />
                </Form.Item>
                <Form.Item name='submitBtn'>
                  <div style={{ textAlign: 'center' }}>
                    <Button type="primary" size="large" htmlType="submit">
                      <CompareIcon /> {t('model.diagnose.metrics.btn.start')}
                    </Button>
                  </div>
                </Form.Item>
              </Form>
            </Panel>
          </div>
          <DefaultStages diagnosing={diagnosing} models={selectedModels} />
        </Col>
      </Row>
    </div >
  )
}

export default Matrics
