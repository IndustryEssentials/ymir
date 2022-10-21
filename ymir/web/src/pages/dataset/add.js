import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Radio, Select, Space, Tag } from 'antd'
import { useParams, useHistory, useLocation } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import useFetch from '@/hooks/useFetch'
import useAddKeywords from '@/hooks/useAddKeywords'
import { IMPORTSTRATEGY } from '@/constants/dataset'

import { urlValidator } from '@/components/form/validators'
import Breadcrumbs from '@/components/common/breadcrumb'
import Uploader from '@/components/form/uploader'
import ProjectDatasetSelect from '@/components/form/projectDatasetSelect'
import Desc from "@/components/form/desc"

import s from './add.less'
import samplePic from '@/assets/sample.png'
import DatasetName from '../../components/form/items/datasetName'
import { FormatDetailModal } from './components/formatDetailModal'

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  INTERNAL: 1,
  COPY: 2,
  NET: 3,
  LOCAL: 4,
  PATH: 5,
})
const types = [
  { id: TYPES.INTERNAL, label: 'internal' },
  { id: TYPES.COPY, label: 'copy' },
  { id: TYPES.NET, label: 'net' },
  { id: TYPES.LOCAL, label: 'local' },
  { id: TYPES.PATH, label: 'path' },
]
const strategies = [
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: 'ignore', },
  { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD, label: 'add', },
  { value: IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE, label: 'exclude', },
]

const Add = (props) => {
  const history = useHistory()
  const { query } = useLocation()
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { id, from, stepKey } = query
  const iterationContext = from === 'iteration'

  const [form] = useForm()
  const [currentType, setCurrentType] = useState(TYPES.INTERNAL)
  const [file, setFile] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(id ? Number(id) : null)
  const [newKeywords, setNewKeywords] = useState([])
  const [strategyOptions, setStrategyOptions] = useState([])
  const [ignoredKeywords, setIgnoredKeywords] = useState([])
  const [{ newer }, checkKeywords] = useFetch('keyword/checkDuplication', { newer: [] })
  const [_, updateKeywords] = useAddKeywords()
  const [addResult, newDataset] = useFetch('dataset/createDataset')
  const [{ items: publicDatasets }, getPublicDatasets] = useFetch('dataset/getInternalDataset', { items: [] })
  const [nameChangedByUser, setNameChangedByUser] = useState(false)
  const [defaultName, setDefaultName] = useState('')
  const netUrl = Form.useWatch('url', form)
  const path = Form.useWatch('path', form)
  const [formatDetailModal, setFormatDetailModal] = useState(false)
  const [updateResult, updateProject] = useFetch('project/updateProject')

  useEffect(() => {
    form.setFieldsValue({ datasetId: null })
    setDefaultName('')
  }, [currentType])

  useEffect(async () => {
    getPublicDatasets()
  }, [])

  useEffect(() => {
    const kws = getSelectedDatasetKeywords()
    checkKeywords(kws)
  }, [selectedDataset])

  useEffect(() => {
    setNewKeywords(newer)
    setIgnoredKeywords([])
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
    const opts = strategies.map(opt => ({ ...opt, label: t(`dataset.add.label_strategy.${opt.label}`) }))
    setStrategyOptions(opts)
  }, [currentType])

  const typeChange = (type) => {
    setCurrentType(type)
    form.setFieldsValue({
      strategy: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE,
    })
  }

  const isType = (type) => {
    return currentType === type
  }

  async function addNewKeywords() {
    if (!newKeywords.length) {
      return
    }
    const result = await updateKeywords(newKeywords)
    return result || message.error(t('keyword.add.failure'))
  }

  async function submit(values) {
    let updateKeywordResult = null
    if (currentType === TYPES.LOCAL && !file) {
      return message.error(t('dataset.add.local.file.empty'))
    }

    if (newKeywords.length && isType(TYPES.INTERNAL)) {
      updateKeywordResult = await addNewKeywords()
      if (updateKeywordResult) {
        addDataset({ ...values, strategy: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE })
      }
    } else {
      addDataset(values)
    }
  }

  function addDataset(values) {
    let params = {
      ...values,
      projectId: pid,
      url: (values.url || '').trim(),
    }
    if (currentType === TYPES.COPY) {
      params.datasetId = params.datasetId[1]
    }
    if (currentType === TYPES.LOCAL) {
      if (file) {
        params.url = file
      } else {
        return message.error(t('dataset.add.local.file.empty'))
      }
    }
    if (isType(TYPES.PATH)) {
      params.path = `/ymir-sharing/${params.path}`
    }
    newDataset(params)
  }

  function onFinishFailed(err) {
    console.log('finish failed: ', err)
  }

  function onInternalDatasetChange(value, { dataset }) {
    setDefaultName(`${dataset.name}`)
    setSelectedDataset(value)
  }

  function setFileDefaultName([file]) {
    const filename = file.name.replace(/\.zip$/i, '')
    setDefaultName(filename)
  }

  function setCopyDefaultName(value, option) {
    const label = value ? option[1]?.label : ''
    const datasetname = label.replace(/\sV\d+\s\(assets: \d+\)/, '')
    setDefaultName(datasetname)
  }

  function addDefaultName(name = '') {
    if (!nameChangedByUser) {
      form.setFieldsValue({ name })
    }
  }

  function updateIgnoredKeywords(e, keywords, isRemove) {
    e.preventDefault()
    const add = old => [...old, ...keywords]
    const remove = old => old.filter(selected => !keywords.includes(selected))
    setIgnoredKeywords(isRemove ? remove : add)
    setNewKeywords(isRemove ? add : remove)
  }

  function renderKeywords(keywords, isIgnoreKeywords) {
    return keywords.length ? keywords.map(key =>
      <Tag className={s.selectedTag} key={key} closable
        onClose={e => updateIgnoredKeywords(e, [key], isIgnoreKeywords)}
      >
        {key}
      </Tag>
    ) : t('common.empty.keywords')
  }

  function getSelectedDatasetKeywords() {
    const set = publicDatasets.find(d => d.id === selectedDataset)
    return set?.keywords || []
  }

  function showFormatDetail() {
    setFormatDetailModal(true)
  }

  const structureTip = t('dataset.add.form.tip.structure', {
    br: <br />,
    pic: <img src={samplePic} />,
    detail: <Button onClick={showFormatDetail}>{t('dataset.add.form.tip.format.detail')}</Button>,
  })

  const renderTip = (type, params = {}) => t(`dataset.add.form.${type}.tip`, {
    ...params,
    br: <br />,
    structure: structureTip,
  })

  return (
    <div className={s.wrapper}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.dataset.add')}>
        <div className={s.formContainer}>
          <Form
            name='datasetImportForm'
            className={s.form}
            {...formLayout}
            form={form}
            onFinish={submit}
            onFinishFailed={onFinishFailed}
          >
            <DatasetName inputProps={{
              onKeyUp: () => setNameChangedByUser(true)
            }} />
            <Form.Item label={t('dataset.add.form.type.label')}>
              <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.INTERNAL}>
                {types.map(type => (
                  <Option value={type.id} key={type.id}>{t(`dataset.add.types.${type.label}`)}</Option>
                ))}
              </Select>
            </Form.Item>

            {isType(TYPES.INTERNAL) ? (
              <>
                <Form.Item
                  label={t('dataset.add.form.internal.label')}
                  tooltip={t('tip.task.filter.datasets')}
                  name='datasetId'
                  initialValue={selectedDataset}
                  rules={isType(TYPES.INTERNAL) ? [
                    { required: true, message: t('dataset.add.form.internal.required') }
                  ] : []}
                >
                  <Select
                    placeholder={t('dataset.add.form.internal.placeholder')}
                    onChange={onInternalDatasetChange}
                    options={publicDatasets.map(dataset => ({
                      value: dataset.id,
                      dataset,
                      label: `${dataset.name} ${dataset.versionName} (Total: ${dataset.assetCount})`
                    }))}>
                  </Select>
                </Form.Item>

                {selectedDataset ?
                  <Form.Item label={t('dataset.import.public.include')}>
                    {newKeywords.length ? <>
                      <h4>
                        {t('dataset.add.internal.newkeywords.label')}
                        <Button type='link' onClick={e => updateIgnoredKeywords(e, newKeywords, false)}>{t('dataset.add.internal.ignore.all')}</Button>
                      </h4>
                      <div>{renderKeywords(newKeywords)}</div>
                    </> : null}
                    {ignoredKeywords.length ? <>
                      <h4>
                        {t('dataset.add.internal.ignorekeywords.label')}
                        <Button type='link' onClick={e => updateIgnoredKeywords(e, ignoredKeywords, true)}>{t('dataset.add.internal.add.all')}</Button>
                      </h4>
                      <div>{renderKeywords(ignoredKeywords, true)}</div>
                    </> : null}
                  </Form.Item>
                  : null}
              </>
            ) : null}
            {isType(TYPES.COPY) ? (
              <Form.Item
                label={t('dataset.add.form.copy.label')}
                name='datasetId'
                rules={[
                  { required: true, message: t('dataset.add.form.copy.required') }
                ]}
              >
                <ProjectDatasetSelect pid={pid} onChange={setCopyDefaultName} placeholder={t('dataset.add.form.copy.placeholder')}></ProjectDatasetSelect>
              </Form.Item>
            ) : null}
            {!isType(TYPES.INTERNAL) ?
              <Form.Item label={t('dataset.add.form.label.label')} name='strategy' initialValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE}>
                <Radio.Group options={strategyOptions.filter(opt => !isType(TYPES.COPY) || opt.value !== IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD)} />
              </Form.Item> : null}
            {isType(TYPES.NET) ? (
              <Form.Item label={t('dataset.add.form.net.label')} required>
                <Form.Item
                  name='url'
                  noStyle
                  rules={[
                    { required: true, message: t('dataset.add.form.net.placeholder') },
                    { validator: urlValidator, }
                  ]}
                >
                  <Input placeholder={t('dataset.add.form.net.placeholder')} max={512} allowClear />
                </Form.Item>
                <p>{renderTip('net')}</p>
              </Form.Item>
            ) : null}

            {isType(TYPES.PATH) ? (
              <Form.Item label={t('dataset.add.form.path.label')} required
                name='path'
                help={renderTip('path')}
                rules={[{ required: true, message: renderTip('path') }]}
              >
                <Input placeholder={t('dataset.add.form.path.placeholder')} max={512} allowClear />
              </Form.Item>
            ) : null}
            {isType(TYPES.LOCAL) ? (
              <Form.Item label={t('dataset.add.form.upload.btn')} required>
                <Uploader
                  onChange={(files, result) => { setFile(result); setFileDefaultName(files) }}
                  max={1024}
                  onRemove={() => setFile('')}
                  info={renderTip('upload', {
                    sample: <a target='_blank' href={'/sample_dataset.zip'}>Sample.zip</a>,
                  })}
                ></Uploader>
              </Form.Item>
            ) : null}
            <Desc form={form} />
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.import')}
                  </Button>
                </Form.Item>
                <Form.Item name='backBtn' noStyle>
                  <Button size="large" onClick={() => history.goBack()}>
                    {t('task.btn.back')}
                  </Button>
                </Form.Item>
              </Space>
            </Form.Item>
          </Form>
        </div>
      </Card>
      <FormatDetailModal title={t('dataset.add.form.tip.format.detail')} visible={formatDetailModal} onCancel={() => setFormatDetailModal(false)} />
    </div>
  )
}

export default Add
