import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Radio, Button, Form, Space, InputNumber, Tag, Tooltip } from "antd"
import { formLayout } from "@/config/antd"
import { useHistory, useParams } from "umi"

import t from "@/utils/t"
import { HIDDENMODULES } from '@/constants/common'
import { string2Array, generateName } from '@/utils/string'
import { OPENPAI_MAX_GPU_COUNT } from '@/constants/common'
import { TYPES } from '@/constants/image'
import { randomNumber } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

import ImageSelect from "@/components/form/imageSelect"
import ModelSelect from "@/components/form/modelSelect"
import SampleRates from "@/components/dataset/sampleRates"
import CheckProjectDirty from "@/components/common/CheckProjectDirty"
import LiveCodeForm from "@/components/form/items/liveCode"
import { removeLiveCodeConfig } from "@/components/form/items/liveCodeConfig"
import DockerConfigForm from "@/components/form/items/dockerConfig"
import OpenpaiForm from "@/components/form/items/openpai"
import DatasetSelect from "@/components/form/datasetSelect"
import Desc from "@/components/form/desc"
import useDuplicatedCheck from "@/hooks/useDuplicatedCheck"
import TrainFormat from "./training/trainFormat"
import SubmitButtons from "./submitButtons"

import styles from "./training/training.less"

const TrainType = [{ value: "detection", label: 'task.train.form.traintypes.detect', checked: true }]

const KeywordsMaxCount = 5

function Train({ query = {}, hidden, ok = () => { }, bottom, allDatasets, datasetCache, ...func }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const { mid, image, iterationId, outputKey, currentStage, test, from } = query
  const stage = string2Array(mid)
  const did = Number(query.did)
  const [selectedKeywords, setSelectedKeywords] = useState([])
  const [dataset, setDataset] = useState({})
  const [trainSet, setTrainSet] = useState(null)
  const [testSet, setTestSet] = useState(null)
  const [validationDataset, setValidationDataset] = useState(null)
  const [trainDataset, setTrainDataset] = useState(null)
  const [testingSetIds, setTestingSetIds] = useState([])
  const [form] = Form.useForm()
  const [seniorConfig, setSeniorConfig] = useState({})
  const [gpu_count, setGPU] = useState(0)
  const [projectDirty, setProjectDirty] = useState(false)
  const [live, setLiveCode] = useState(false)
  const [openpai, setOpenpai] = useState(false)
  const checkDuplicated = useDuplicatedCheck(submit)
  const [sys, getSysInfo] = useFetch('common/getSysInfo', {})
  const [project, getProject] = useFetch('project/getProject', {})
  const [updated, updateProject] = useFetch('project/updateProject')
  const [fromCopy, setFromCopy] = useState(false)

  const selectOpenpai = Form.useWatch('openpai', form)
  const [showConfig, setShowConfig] = useState(false)
  const iterationContext = from === 'iteration'

  const renderRadio = (types) => <Radio.Group options={types.map(type => ({ ...type, label: t(type.label) }))} />

  useEffect(() => {
    getSysInfo()
    getProject({ id: pid })
  }, [])

  useEffect(() => {
    setGPU(sys.gpu_count)
    if (!HIDDENMODULES.OPENPAI) {
      setOpenpai(!!sys.openpai_enabled)
    }
  }, [sys])

  useEffect(() => {
    setGPU(selectOpenpai ? OPENPAI_MAX_GPU_COUNT : sys.gpu_count || 0)
  }, [selectOpenpai])

  useEffect(() => {
    setTestingSetIds(project?.testingSets || [])
    iterationContext && setSelectedKeywords(project?.keywords || [])
  }, [project])

  useEffect(() => {
    if (did && allDatasets?.length) {
      const isValid = allDatasets.some(ds => ds.id === did)
      const visibleValue = isValid ? did : null
      setTrainSet(visibleValue)
      form.setFieldsValue({ datasetId: visibleValue })
    }
  }, [did, allDatasets])

  useEffect(() => {
    did && func.getDataset(did)
  }, [did])

  useEffect(() => {
    const dst = datasetCache[did]
    dst && setDataset(dst)
  }, [datasetCache])

  useEffect(() => {
    pid && func.getDatasets(pid)
  }, [pid])

  useEffect(() => {
    trainDataset &&
      !iterationContext &&
      !fromCopy &&
      setAllKeywords()
    if (!trainDataset && fromCopy) {
      setSelectedKeywords([])
      form.setFieldsValue({ keywords: [] })
    }
  }, [trainDataset])

  useEffect(() => {
    const state = location.state

    if (state?.record) {
      setFromCopy(true)
      const { task: { parameters, config }, description, } = state.record
      const {
        dataset_id,
        validation_dataset_id,
        strategy,
        docker_image,
        docker_image_id,
        model_id,
        model_stage_id,
        keywords,
      } = parameters
      form.setFieldsValue({
        datasetId: dataset_id,
        keywords: keywords,
        testset: validation_dataset_id,
        gpu_count: config.gpu_count,
        modelStage: [model_id, model_stage_id],
        image: docker_image_id + ',' + docker_image,
        strategy,
        description,
      })
      setTimeout(() => setConfig(config), 500)
      setTestSet(validation_dataset_id)
      setTrainSet(dataset_id)
      setSelectedKeywords(keywords)
      setShowConfig(true)

      history.replace({ state: {} })
    }
  }, [location.state])

  function setAllKeywords() {
    const kws = trainDataset?.gt?.keywords
    setSelectedKeywords(kws)
    form.setFieldsValue({ keywords: kws })
  }

  function trainSetChange(value, option) {
    setTrainSet(value)
    setTrainDataset(option?.dataset)
  }
  function validationSetChange(value, option) {
    setTestSet(value)
    setValidationDataset(option?.dataset)
  }

  function imageChange(_, image = {}) {
    const { configs } = image
    const configObj = (configs || []).find(conf => conf.type === TYPES.TRAINING) || {}
    if (!HIDDENMODULES.LIVECODE) {
      setLiveCode(image.liveCode || false)
    }
    setConfig(removeLiveCodeConfig(configObj.config))
  }

  function setConfig(config = {}) {
    setSeniorConfig(config)
  }

  const onFinish = () => checkDuplicated(trainDataset, validationDataset)

  async function submit(strategy) {
    const values = form.getFieldsValue()
    const config = {
      ...values.hyperparam?.reduce(
        (prev, { key, value }) => key !== '' && value !== '' ? { ...prev, [key]: value } : prev,
        {}),
      ...(values.live || {}),
    }
    values.trainFormat && (config['export_format'] = values.trainFormat)

    const gpuCount = form.getFieldValue('gpu_count')

    config['gpu_count'] = gpuCount || 0

    const img = (form.getFieldValue('image') || '').split(',')
    const imageId = Number(img[0])
    const image = img[1]
    const params = {
      ...values,
      strategy,
      name: 'group_' + randomNumber(),
      projectId: pid,
      keywords: iterationContext ? project.keywords : values.keywords,
      image,
      imageId,
      config,
    }
    const result = await func.train(params)
    result && ok(result.result_model)
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  const matchKeywords = dataset => dataset.keywords.some(kw => selectedKeywords.includes(kw))
  const notTestingSet = id => !testingSetIds.includes(id)
  const trainsetFilters = datasets => datasets.filter(ds => {
    const notTestSet = ds.id !== testSet
    return notTestSet && notTestingSet(ds.id)
  })

  const validationSetFilters = datasets => datasets.filter(ds => {
    const notTrainSet = ds.id !== trainSet
    return matchKeywords(ds) && notTrainSet && notTestingSet(ds.id)
  })

  const getCheckedValue = (list) => list.find((item) => item.checked)["value"]
  const initialValues = {
    name: generateName('train_model'),
    datasetId: did ? did : undefined,
    testset: Number(test) ? Number(test) : undefined,
    image: image ? parseInt(image) : undefined,
    modelStage: stage,
    trainType: getCheckedValue(TrainType),
    gpu_count: 1,
  }
  return (
    <div>
      <div hidden={hidden}>
        <CheckProjectDirty
          style={{ marginBottom: 20, width: '100%' }}
          pid={pid}
          initialCheck={true}
          callback={(dirty) => setProjectDirty(dirty)}
        />
      </div>
      <Form
        name='trainForm'
        className={styles.form}
        {...formLayout}
        form={form}
        initialValues={initialValues}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
      >
        <div hidden={hidden}>
          <Form.Item name='image' label={t('task.train.form.image.label')} rules={[
            { required: true, message: t('task.train.form.image.required') }
          ]} tooltip={t('tip.task.train.image')}>
            <ImageSelect placeholder={t('task.train.form.image.placeholder')} onChange={imageChange} />
          </Form.Item>
          <OpenpaiForm form={form} openpai={openpai} />
          <Form.Item
            label={t('task.train.form.trainsets.label')}
            required
            name="datasetId"
            rules={[
              { required: true, message: t('task.train.form.trainset.required') },
            ]}
          >
            <DatasetSelect
              pid={pid}
              filters={trainsetFilters}
              onChange={trainSetChange}
            />
          </Form.Item>
          {iterationContext ? <Form.Item label={t('task.train.form.keywords.label')}>
            {project?.keywords?.map(keyword => <Tag key={keyword}>{keyword}</Tag>)}
          </Form.Item> :
            <Form.Item
              label={t('task.train.form.keywords.label')}
              name="keywords"
              rules={[
                { required: true, message: t('project.add.form.keyword.required') }
              ]}
              tooltip={t('tip.task.filter.keywords')}
              help={trainDataset && selectedKeywords.length !== trainDataset.gt.keywords.length ?
                <Button type="link" onClick={() => setAllKeywords()}>{t('dataset.train.all.train.target')}</Button>
                : null}
            >
              <Select mode="multiple" showArrow allowClear
                placeholder={t('project.add.form.keyword.required')}
                onChange={setSelectedKeywords}
                options={(trainDataset?.gt?.keywords || []).map(k => ({ label: k, value: k }))}
                maxTagCount={KeywordsMaxCount}
                maxTagPlaceholder={<Tooltip
                  trigger='hover'
                  color='white'
                  title={selectedKeywords.slice(KeywordsMaxCount).map(k => <Tag key={k}>{k}</Tag>)}
                >
                  {selectedKeywords.length - KeywordsMaxCount}+
                </Tooltip>}
              />
            </Form.Item>}
          <Form.Item label={t('dataset.train.form.samples')}>
            <SampleRates keywords={selectedKeywords} dataset={trainDataset} negative />
          </Form.Item>
          <Form.Item
            label={t('task.train.form.testsets.label')}
            name="testset"
            rules={[
              { required: true, message: t('task.train.form.testset.required') },
            ]}
            tooltip={t('tip.task.filter.testsets')}
          >
            <DatasetSelect
              pid={pid}
              filters={validationSetFilters}
              placeholder={t('task.train.form.test.datasets.placeholder')}
              onChange={validationSetChange}
            />
          </Form.Item>
          <Form.Item
            label={t('task.detail.label.premodel')}
            name="modelStage"
            tooltip={t('tip.task.train.model')}
          >
            <ModelSelect placeholder={t('task.train.form.model.placeholder')} pid={pid} />
          </Form.Item>
          <Form.Item
            hidden
            label={t('task.train.form.traintype.label')}
            name="trainType"
          >
            {renderRadio(TrainType)}
          </Form.Item>

          <Form.Item
            label={t('task.gpu.count')}
            tooltip={t('tip.task.filter.gpucount')}
          >
            <Form.Item
              noStyle
              name="gpu_count"
              rules={[
                {
                  validator: (rules, value) => value <= gpu_count ?
                    Promise.resolve() :
                    Promise.reject(),
                  message: t('task.gpu.tip', { count: gpu_count })
                }
              ]}
            >
              <InputNumber min={0} max={gpu_count} precision={0} />
            </Form.Item>
            <span style={{ marginLeft: 20 }}>{t('task.gpu.tip', { count: gpu_count })}</span>
          </Form.Item>
          {live ? <Form.Item
            label={t('task.train.export.format')}
            tooltip={t('tip.train.export.format')}
            name='trainFormat'
            initialValue={'ark:raw'}>
            <TrainFormat />
          </Form.Item> : null}
          <LiveCodeForm form={form} live={live} />
          <DockerConfigForm show={showConfig} seniorConfig={seniorConfig} form={form} />
          <Desc form={form} />
        </div>
        <Form.Item wrapperCol={{ offset: 8 }}>
          {bottom ? bottom : <SubmitButtons label="common.action.train" />}
        </Form.Item>
      </Form>
    </div>
  )
}

const props = (state) => {
  return {
    allDatasets: state.dataset.allDatasets,
    datasetCache: state.dataset.dataset,
  }
}

const dis = (dispatch) => {
  return {
    getDatasets(pid, force = true) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force },
      })
    },
    getDataset(id, force) {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
      })
    },
    clearCache() {
      return dispatch({ type: "model/clearCache", })
    },
    train(payload) {
      return dispatch({
        type: "task/train",
        payload,
      })
    },
    updateIteration(params) {
      return dispatch({
        type: 'iteration/updateIteration',
        payload: params,
      })
    },
  }
}

export default connect(props, dis)(Train)
