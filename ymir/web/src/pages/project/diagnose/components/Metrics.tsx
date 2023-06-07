import { ViewProps, EvaluationResult, TabIdType } from '.'
import { FC, useCallback, useEffect, useState } from 'react'
import { Button, Form, Row, Col, Radio, Slider, Select, InputNumber, Space, Tag, RadioChangeEvent } from 'antd'
import { useLocation, useSelector } from 'umi'

import t from '@/utils/t'
import { ObjectType, isDetection, isSemantic, isSegmentation } from '@/constants/objectType'

import Panel from '@/components/form/panel'
import SingleMetircView from './SingleMetircView'
import CurveView from './CurveView'
import PView from './PRView'
import View from './View'
import DefaultStages from './DefaultStages'
import Tip from '@/components/form/SingleTip'

import s from '../index.less'
import { CompareIcon } from '@/components/common/Icons'
import useRequest from '@/hooks/useRequest'
import CKSelector from './CKSelector'
import { ValidateErrorEntity } from 'rc-field-form/lib/interface'
import ModelVersionName from '@/components/result/ModelVersionName'
import VersionName from '@/components/result/VersionName'
import ReactJson from 'react-json-view'
import IouSlider from './IouSlider'
import { getInferClassesFromResult } from './common'
import { Prediction } from '@/constants'
type Props = {
  prediction: Prediction
}
type TabType = {
  value: TabIdType
  component: FC<ViewProps>
  ck?: boolean
}

const metricsTabs: TabType[] = [
  { value: 'ap', component: SingleMetircView, ck: true },
  { value: 'iou', component: SingleMetircView },
  { value: 'acc', component: SingleMetircView },
  { value: 'maskap', component: SingleMetircView },
  { value: 'boxap', component: SingleMetircView },
  { value: 'curve', component: CurveView },
  { value: 'rp', component: PView },
  { value: 'pr', component: PView },
]

const getTabs = (type = ObjectType.ObjectDetection) => {
  const types = {
    [ObjectType.ObjectDetection]: ['ap', 'curve', 'rp', 'pr'],
    [ObjectType.SemanticSegmentation]: ['iou', 'acc'],
    [ObjectType.InstanceSegmentation]: ['maskap', 'boxap'],
    [ObjectType.MultiModal]: ['ap', 'curve', 'rp', 'pr'],
  }
  return metricsTabs.filter(({ value }) => types[type].includes(value))
}

const xAxisOptions = [
  { key: 'dataset', value: false },
  { key: 'keyword', value: true },
]

const kwTypes = [
  { label: 'keyword.add.name.label', value: false },
  { label: 'keyword.ck.label', value: true },
]

const Matrics: FC<Props> = ({ prediction }) => {
  const [tabs, setTabs] = useState<TabType[]>([])
  const { state } = useLocation<{ mid: number }>()
  const [form] = Form.useForm()
  const [averageIou, setaverageIou] = useState(true)
  const [confidence, setConfidence] = useState(0.3)
  const [confidenceChanged, setConfidenceChanged] = useState(false)
  const [selectedMetric, setSelectedMetric] = useState<TabIdType>('ap')
  const [prRate, setPrRate] = useState<[number, number]>([0.8, 0.95])
  const [keywords, setKeywords] = useState<string[]>([])
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([])
  const [subCks, setSubCks] = useState<string[]>([])
  const [ck, setCk] = useState<boolean>(false)
  const [kws, setKws] = useState<string[]>([])
  const [xAxis, setXAsix] = useState(xAxisOptions[0].value)
  const [diagnosis, setDiagnosis] = useState<EvaluationResult>()
  const [diagnosing, setDiagnosing] = useState(false)
  const [kwFilter, setKwFilter] = useState<{ ck: boolean; keywords: string[] }>({
    ck: false,
    keywords: [],
  })
  const { data: remoteData, run: fetchDiagnosis } = useRequest<EvaluationResult, [YParams.EvaluationParams]>('prediction/evaluate')

  const selectedCK = Form.useWatch('ck', form)
  const model = useSelector(({ model }) => model.model[prediction.inferModelId[0].toString()])
  const dataset = useSelector(({ dataset }) => dataset.dataset[prediction.inferDatasetId.toString()])

  useEffect(() => {
    if (prediction?.type) {
      const tabs = getTabs(prediction.type)
      setTabs(tabs)
      setSelectedMetric(tabs[0].value)
    }
  }, [prediction?.type])

  useEffect(() => remoteData && setDiagnosis(remoteData), [remoteData])

  useEffect(() => {
    if (state?.mid) {
      form.setFieldsValue({
        stage: [state.mid],
      })
    }
  }, [state])

  useEffect(() => {
    if (diagnosis && prediction) {
      const kws = prediction.inferClass || getInferClassesFromResult(diagnosis[prediction.id], selectedMetric, !isSemantic(prediction.type)) || []
      setKeywords(kws)
    } else {
      setKeywords([])
    }
  }, [prediction, diagnosis])

  useEffect(() => {
    // calculate ck
    const cks = diagnosis
      ? Object.values(diagnosis)
          .filter((tru) => tru)
          .map((item) => Object.keys(item?.sub_cks || {}))
          .flat()
      : []

    setSubCks([...new Set(cks)])
  }, [diagnosis])

  useEffect(() => {
    setKws(!ck ? keywords : subCks)
  }, [ck, keywords, subCks])

  useEffect(() => {
    setDiagnosing(!!diagnosis)
    setSelectedKeywords([])
  }, [diagnosis])

  useEffect(() => {
    setKwFilter({
      keywords: selectedKeywords?.length ? selectedKeywords : kws,
      ck,
    })
  }, [selectedKeywords, kws])

  useEffect(() => {
    prediction && diagnose()
  }, [prediction])

  const diagnose = () => {
    fetchDiagnosis({
      pid: prediction.projectId,
      predictionId: prediction.id,
      curve: false,
      averageIou: true,
      confidence,
    })
    setConfidenceChanged(false)
  }

  function onFinishFailed(errorInfo: ValidateErrorEntity) {
    console.log('Failed:', errorInfo)
  }

  function metricsChange({ target: { value } }: RadioChangeEvent) {
    setSelectedMetric(value)
  }

  function prRateChange(value: [number, number]) {
    setPrRate(value)
  }

  function xAxisChange({ target: { value } }: RadioChangeEvent) {
    setXAsix(value)
  }

  function kwChange(values: string[]) {
    setSelectedKeywords(values)
  }

  function renderView() {
    if (!prediction || !dataset || !model) {
      return
    }
    const panel = tabs.find(({ value }) => selectedMetric === value)
    if (!panel) {
      return
    }
    const Viewer = View(panel.component)
    return (
      <Viewer
        type={panel.value}
        predictions={[prediction]}
        models={[model]}
        datasets={[dataset]}
        data={diagnosis}
        averageIou={averageIou}
        p2r={selectedMetric === 'pr'}
        prRate={prRate}
        xByClasses={xAxis}
        kw={kwFilter}
      />
    )
  }

  const renderFilterPanel = () => (
    <div className={s.filterPanel}>
      <Space size={20} style={{ marginBottom: 10 }}>
        <span>{t('model.diagnose.metrics.view.label')}</span>
        <Radio.Group
          value={selectedMetric}
          options={tabs.map((item, index) => ({
            ...item,
            label: t(`model.diagnose.medtric.tabs.${item.value}`),
            disabled: isDetection(prediction?.type) && averageIou && index > 0,
          }))}
          onChange={metricsChange}
        />
        <div hidden={!['rp', 'pr'].includes(selectedMetric)}>
          <Slider className={s.prRate} style={{ width: 200 }} min={0} max={1} value={prRate} range={true} onChange={prRateChange} step={0.05} />
        </div>
      </Space>
      <Row gutter={20}>
        <Col>
          <Select
            value={ck}
            options={kwTypes
              .filter((type) => {
                const tab = tabs.find(({ value }) => selectedMetric === value)
                return tab?.ck || !type.value
              })
              .map(({ label, value }) => ({ value, label: t(label) }))}
            onChange={setCk}
          ></Select>
        </Col>
        <Col flex={1}>
          {kwTypes[0].value === ck ? (
            <Select
              style={{ width: '100%' }}
              mode={ck ? undefined : 'multiple'}
              value={selectedKeywords}
              options={kws.map((kw) => ({ label: kw, value: kw }))}
              placeholder={t(ck ? 'model.diagnose.metrics.ck.placeholder' : 'model.diagnose.metrics.keyword.placeholder')}
              showArrow
              onChange={kwChange}
            ></Select>
          ) : (
            <Tag>{selectedCK}</Tag>
          )}
        </Col>
        <Col>
          <Space size={20}>
            <span>{t('model.diagnose.metrics.dimension.label')}</span>
            <Radio.Group
              defaultValue={xAxisOptions[0].value}
              options={xAxisOptions.map(({ key, value }) => ({ value, label: t(`model.diagnose.metrics.x.${key}`) }))}
              onChange={xAxisChange}
            />
          </Space>
        </Col>
      </Row>
    </div>
  )

  const renderViewPanel = () => <div className={s.metricsPanel}>{renderView()}</div>

  const renderIouOptionLabel = (type: string) => (
    <>
      {t(`model.diagnose.form.iou.${type}`)}
      <Tip className={s.iouTip} content={t(`model.diagnose.form.iou.${type}.tip`)} placement="top" arrowPointAtCenter />
    </>
  )

  const iouOptions = [
    { value: true, label: renderIouOptionLabel('everage') },
    { value: false, label: renderIouOptionLabel('single') },
  ]

  // todo form initial values
  const initialValues = {
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
            <Panel label={'Metrics'} toogleVisible={false}>
              <Form
                className={s.form}
                form={form}
                layout="vertical"
                initialValues={initialValues}
                onFinish={diagnose}
                onFinishFailed={onFinishFailed}
                labelAlign="left"
                colon={false}
              >
                <Form.Item label={t('pred.metrics.prediction.select.label')}>
                  <p>
                    <span>{t('model.diagnose.label.model')}：</span>
                    <ModelVersionName id={prediction.inferModelId[0]} stageId={prediction.inferModelId[1]} />
                  </p>
                  <p>
                    <span>{t('model.diagnose.label.testing_dataset')}: </span>
                    <VersionName id={prediction.inferDatasetId} />
                  </p>
                  <div>
                    <p>{t('model.diagnose.label.config')}</p>
                    <ReactJson src={prediction.task.config} collapsed={true} />
                  </div>
                </Form.Item>
                {!isSemantic(prediction?.type) ? (
                  <Form.Item label={t('model.diagnose.form.confidence')} name="confidence">
                    <InputNumber
                      step={0.0005}
                      min={0.0005}
                      max={0.9995}
                      onChange={(value) => {
                        setConfidence(value)
                        setConfidenceChanged(true)
                      }}
                    />
                  </Form.Item>
                ) : null}
                {!isSemantic(prediction?.type) ? (
                  <Form.Item style={{ textAlign: 'center' }}>
                    <Button htmlType="submit" type="primary" disabled={!confidenceChanged} onClick={() => diagnose()}>
                      <CompareIcon /> {t('model.diagnose.metrics.btn.retry')}
                    </Button>
                  </Form.Item>
                ) : null}
              </Form>
            </Panel>
          </div>
        </Col>
      </Row>
    </div>
  )
}

export default Matrics
