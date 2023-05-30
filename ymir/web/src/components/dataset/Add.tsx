import { FC, MouseEvent, ReactElement, useEffect, useState } from 'react'
import { Alert, Button, Card, CardProps, CheckboxOptionType, Form, Input, message, Radio, Select, Space, Tag } from 'antd'
import { useParams, useHistory, useSelector } from 'umi'

import { formLayout } from '@/config/antd'
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import useRequest from '@/hooks/useRequest'
import { IMPORTSTRATEGY } from '@/constants/dataset'
import { ObjectType } from '@/constants/project'

import { urlValidator } from '@/components/form/validators'
import Uploader, { UploadFile } from '@/components/form/uploader'
import ProjectDatasetSelect, { DataNodeType } from '@/components/form/ProjectDatasetSelect'
import Desc from '@/components/form/desc'
import DatasetName from '@/components/form/items/DatasetName'
import FormatDetailModal from '@/components/dataset/FormatDetailModal'
import Dataset from '@/components/form/option/Dataset'

import s from './add.less'
import DetSamplePic from '@/assets/sample.png'
import SegSamplePic from '@/assets/sample_seg.png'
import { ValidateErrorEntity } from 'rc-field-form/lib/interface'
import TypeSelector from './add/TypeSelector'
import { Types } from './add/AddTypes'
import { List } from '@/models/typings/common.d'
import { Dataset as DatasetType } from '@/constants'
import { isDetection } from '@/constants/objectType'

type DatasetOptionType = {
  value: number
  label: string | ReactElement
  dataset: DatasetType
}
type Props = Omit<CardProps, 'id'> & {
  id?: number
  from?: string
  stepKey?: string
  back?: (e: MouseEvent<HTMLElement>) => void
}

const { useForm } = Form

const strategies: { value: string | number; label: string }[] = [
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD, label: 'add' },
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: 'ignore' },
  { value: IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE, label: 'exclude' },
]

const Add: FC<Props> = ({ id, from, stepKey, back, ...props }) => {
  const history = useHistory()
  const pageParams = useParams<{ id?: string }>()
  const pid = Number(pageParams.id)
  const iterationContext = from === 'iteration'

  const [form] = useForm()
  const [currentType, setCurrentType] = useState(Types.LOCAL)
  const [file, setFile] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(id ? Number(id) : 0)
  const [newKeywords, setNewKeywords] = useState<string[]>([])
  const [strategyOptions, setStrategyOptions] = useState<CheckboxOptionType[]>([])
  const [ignoredKeywords, setIgnoredKeywords] = useState<string[]>([])
  const { data: { newer } = {}, run: checkKeywords } = useRequest<{ newer: string[] }>('keyword/checkDuplication')
  const [addResult, newDataset] = useFetch('dataset/createDataset')
  const { data: publicDatasets = [], run: getPublicDatasets } = useRequest<DatasetType[]>('dataset/getInternalDataset')
  const { runAsync: addKeywords } = useRequest<{}, [{ keywords: string[]; dry_run?: boolean }]>('keyword/addKeywords')
  const [nameChangedByUser, setNameChangedByUser] = useState(false)
  const [defaultName, setDefaultName] = useState('')
  const netUrl = Form.useWatch<string>('url', form)
  const path = Form.useWatch<string>('path', form)
  const [formatDetailModal, setFormatDetailModal] = useState(false)
  const project = useSelector(({ project }) => project.projects[pid] || {})
  const { run: getProject } = useRequest('project/getProject', {
    loading: false,
    refreshDeps: [pid],
    ready: !!pid,
  })
  const [updateResult, updateProject] = useFetch('project/updateProject')
  const [sampleZip, setSampleZip] = useState('/sample_dataset.zip')
  const [samplePic, setSamplePic] = useState(DetSamplePic)

  useEffect(() => {
    getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    !isDetection(project.type) && (setSampleZip('/sample_dataset_seg.zip'), setSamplePic(SegSamplePic))
  }, [project])

  useEffect(() => {
    form.setFieldsValue({ did: null })
    setDefaultName('')
  }, [currentType])

  useEffect(() => {
    getPublicDatasets()
  }, [])

  useEffect(() => {
    const dataset = publicDatasets.find(({ id }) => id === selectedDataset)
    const kws = dataset?.keywords || []
    kws.length && checkKeywords(kws)
    dataset && setDefaultName(dataset.name)
  }, [selectedDataset])

  useEffect(() => {
    if (newer) {
      setNewKeywords(newer)
      setIgnoredKeywords([])
    }
  }, [newer])

  useEffect(() => {
    const filename = (netUrl || '').replace(/^.+\/([^\/]+)\.zip$/, '$1')
    setDefaultName(filename)
  }, [netUrl])

  useEffect(() => {
    if (typeof path === 'undefined') {
      return
    }
    const matchfinalDir = path.match(/[^\/]+$/) || []
    const finalDir = matchfinalDir[0]
    setDefaultName(finalDir)
  }, [path])

  useEffect(() => addDefaultName(defaultName), [defaultName])

  useEffect(() => {
    if (addResult) {
      message.success(t('dataset.add.success.msg'))
      if (iterationContext && stepKey) {
        return updateProject({ id: pid, [stepKey]: addResult.id })
      }
      const group = addResult.dataset_group_id || ''
      history.replace(`/home/project/${pid}/dataset#${group}`)
    }
  }, [addResult])

  useEffect(() => {
    if (updateResult) {
      history.replace(`/home/project/${pid}/iterations`)
    }
  }, [updateResult])

  useEffect(() => {
    const opts = strategies.map((opt) => ({
      ...opt,
      label: t(`dataset.add.label_strategy.${opt.label}`),
    }))
    setStrategyOptions(opts)
  }, [currentType])

  const typeChange = (type: number) => {
    setCurrentType(type)
    form.setFieldsValue({
      strategy: IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD,
    })
  }

  const isType = (type: Types) => currentType === type

  async function submit(values: { [key: string]: any }) {
    if (currentType === Types.LOCAL && !file) {
      return message.error(t('dataset.add.local.file.empty'))
    }

    if (newKeywords.length && isType(Types.INTERNAL)) {
      const updateKeywordResult = await addKeywords({ keywords: newKeywords })
      if (updateKeywordResult) {
        addDataset({
          ...values,
          strategy: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE,
        })
      } else {
        message.error(t('keyword.add.failure'))
      }
    } else {
      addDataset(values)
    }
  }

  function addDataset(values: { [x: string]: any; strategy?: IMPORTSTRATEGY; url?: any }) {
    let params: { [key: string]: any } = {
      ...values,
      pid,
      url: (values.url || '').trim(),
    }
    if (currentType === Types.COPY) {
      params.did = params.did[1]
    }
    if (currentType === Types.LOCAL) {
      if (file) {
        params.url = file
      } else {
        return message.error(t('dataset.add.local.file.empty'))
      }
    }
    if (isType(Types.PATH)) {
      params.path = `/ymir-sharing/${params.path}`
    }
    newDataset(params)
  }

  function onFinishFailed(err: ValidateErrorEntity) {
    console.log('finish failed: ', err)
  }

  function onInternalDatasetChange(id: number) {
    setSelectedDataset(id)
  }

  function setFileDefaultName([file]: UploadFile[]) {
    const filename = file.name.replace(/\.zip$/i, '')
    setDefaultName(filename)
  }

  function addDefaultName(name = '') {
    if (!nameChangedByUser) {
      form.setFieldsValue({ name })
    }
  }

  function updateIgnoredKeywords(e: MouseEvent, keywords: string[], isRemove?: boolean) {
    e.preventDefault()
    const add = (old: string[]) => [...old, ...keywords]
    const remove = (old: string[]) => old.filter((selected) => !keywords.includes(selected))
    setIgnoredKeywords(isRemove ? remove : add)
    setNewKeywords(isRemove ? add : remove)
  }

  function renderKeywords(keywords: string[], isIgnoreKeywords?: boolean) {
    return keywords.length
      ? keywords.map((key) => (
          <Tag className={s.selectedTag} key={key} closable onClose={(e) => updateIgnoredKeywords(e, [key], isIgnoreKeywords)}>
            {key}
          </Tag>
        ))
      : t('common.empty.keywords')
  }

  const structureTip = t('dataset.add.form.tip.structure', {
    br: <br />,
    pic: <img src={samplePic} />,
    detail: <Button onClick={() => setFormatDetailModal(true)}>{t('dataset.add.form.tip.format.detail')}</Button>,
  })

  const renderTip = (type: string, params = {}) =>
    t(`dataset.add.form.${type}.tip`, {
      ...params,
      br: <br />,
      structure: structureTip,
      format: project.type === ObjectType.ObjectDetection ? 'Pascal VOC' : 'Coco',
    })

  return (
    <Card className={s.container} title={t('breadcrumbs.dataset.add')} {...props}>
      <div className={s.formContainer}>
        <Alert message={t('dataset.add.top.warning')} type="warning" style={{ marginBottom: 20 }} />
        <Form name="datasetImportForm" className={s.form} {...formLayout} form={form} onFinish={submit} onFinishFailed={onFinishFailed}>
          <DatasetName
            inputProps={{
              onKeyUp: () => setNameChangedByUser(true),
            }}
          />
          <Form.Item label={t('dataset.add.form.type.label')} initialValue={Types.LOCAL}>
            <TypeSelector onChange={typeChange} />
          </Form.Item>

          {isType(Types.INTERNAL) ? (
            <>
              <Form.Item
                label={t('dataset.add.form.internal.label')}
                tooltip={t('tip.task.filter.datasets')}
                name="did"
                initialValue={selectedDataset}
                rules={
                  isType(Types.INTERNAL)
                    ? [
                        {
                          required: true,
                          message: t('dataset.add.form.internal.required'),
                        },
                      ]
                    : []
                }
              >
                <Select
                  placeholder={t('dataset.add.form.internal.placeholder')}
                  onChange={onInternalDatasetChange}
                  options={publicDatasets.map((dataset) => ({
                    value: dataset.id,
                    dataset,
                    label: <Dataset dataset={dataset} />,
                  }))}
                ></Select>
              </Form.Item>

              {selectedDataset && newKeywords.length ? (
                <Form.Item label={t('dataset.import.public.include')}>
                  <>
                    <h4>
                      {t('dataset.add.internal.newkeywords.label')}
                      <Button type="link" onClick={(e) => updateIgnoredKeywords(e, newKeywords, false)}>
                        {t('dataset.add.internal.ignore.all')}
                      </Button>
                    </h4>
                    <div>{renderKeywords(newKeywords)}</div>
                  </>
                  {ignoredKeywords.length ? (
                    <>
                      <h4>
                        {t('dataset.add.internal.ignorekeywords.label')}
                        <Button type="link" onClick={(e) => updateIgnoredKeywords(e, ignoredKeywords, true)}>
                          {t('dataset.add.internal.add.all')}
                        </Button>
                      </h4>
                      <div>{renderKeywords(ignoredKeywords, true)}</div>
                    </>
                  ) : null}
                </Form.Item>
              ) : null}
            </>
          ) : null}
          {isType(Types.COPY) ? (
            <Form.Item
              label={t('dataset.add.form.copy.label')}
              name="did"
              rules={[
                {
                  required: true,
                  message: t('dataset.add.form.copy.required'),
                },
              ]}
            >
              <ProjectDatasetSelect
                onChange={(_, option) => {
                  const dataset = option[1] ? option[1].dataset : null
                  const label = dataset ? `${dataset.name}` : ''
                  setDefaultName(label)
                }}
                placeholder={t('dataset.add.form.copy.placeholder')}
              ></ProjectDatasetSelect>
            </Form.Item>
          ) : null}
          {!isType(Types.INTERNAL) ? (
            <Form.Item label={t('dataset.add.form.label.label')} name="strategy" initialValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD}>
              <Radio.Group options={strategyOptions.filter((opt) => !isType(Types.COPY) || opt.value !== IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)} />
            </Form.Item>
          ) : null}
          {isType(Types.NET) ? (
            <Form.Item label={t('dataset.add.form.net.label')} required>
              <Form.Item
                name="url"
                noStyle
                rules={[
                  {
                    required: true,
                    message: t('dataset.add.form.net.placeholder'),
                  },
                  { validator: urlValidator },
                ]}
              >
                <Input placeholder={t('dataset.add.form.net.placeholder')} max={512} allowClear />
              </Form.Item>
              <p>{renderTip('net')}</p>
            </Form.Item>
          ) : null}

          {isType(Types.PATH) ? (
            <Form.Item
              label={t('dataset.add.form.path.label')}
              required
              name="path"
              help={renderTip('path')}
              rules={[{ required: true, message: renderTip('path') }]}
            >
              <Input placeholder={t('dataset.add.form.path.placeholder')} max={512} allowClear />
            </Form.Item>
          ) : null}
          {isType(Types.LOCAL) ? (
            <Form.Item label={t('dataset.add.form.upload.btn')} required>
              <Uploader
                onChange={({ fileList }) => {
                  const file = fileList[0]
                  setFile(file.url || '')
                  setFileDefaultName(fileList)
                }}
                max={1024}
                onRemove={() => setFile('')}
                info={renderTip('upload', {
                  sample: (
                    <a target="_blank" href={sampleZip}>
                      Sample.zip
                    </a>
                  ),
                })}
              ></Uploader>
            </Form.Item>
          ) : null}
          <Desc />
          <Form.Item wrapperCol={{ offset: 8 }}>
            <Space size={20}>
              <Form.Item name="submitBtn" noStyle>
                <Button type="primary" size="large" htmlType="submit">
                  {t('common.action.import')}
                </Button>
              </Form.Item>
              <Form.Item name="backBtn" noStyle>
                <Button size="large" onClick={(e) => (back ? back(e) : history.goBack())}>
                  {t('task.btn.back')}
                </Button>
              </Form.Item>
            </Space>
          </Form.Item>
        </Form>
      </div>
      <FormatDetailModal title={t('dataset.add.form.tip.format.detail')} visible={formatDetailModal} onCancel={() => setFormatDetailModal(false)} />
    </Card>
  )
}

export default Add
