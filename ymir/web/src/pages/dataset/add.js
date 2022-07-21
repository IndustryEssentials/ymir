import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Radio, Row, Col, Select, Space, Tag } from 'antd'
import { connect } from 'dva'
import { Link, useParams, useHistory } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import { IMPORTSTRATEGY } from '@/constants/dataset'
import Uploader from '@/components/form/uploader'
import { randomNumber } from '@/utils/number'
import { urlValidator } from '@/components/form/validators'
import s from './add.less'
import Breadcrumbs from '@/components/common/breadcrumb'
import { TipsIcon } from '@/components/common/icons'
import ProjectDatasetSelect from '@/components/form/projectDatasetSelect'
import useAddKeywords from '@/hooks/useAddKeywords'
import useFetch from '@/hooks/useFetch'
import samplePic from '@/assets/sample.png'

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  INTERNAL: 1,
  COPY: 2,
  NET: 3,
  LOCAL: 4,
  PATH: 5,
})


const Add = (props) => {
  const history = useHistory()
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { id } = history.location.query
  const types = [
    { id: TYPES.INTERNAL, label: t('dataset.add.types.internal') },
    { id: TYPES.COPY, label: t('dataset.add.types.copy') },
    { id: TYPES.NET, label: t('dataset.add.types.net') },
    { id: TYPES.LOCAL, label: t('dataset.add.types.local') },
    { id: TYPES.PATH, label: t('dataset.add.types.path') },
  ]
  const labelOptions = [
    { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: t('dataset.add.label_strategy.ignore'), },
    { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_AUTO_ADD, label: t('dataset.add.label_strategy.add'), },
    { value: IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE, label: t('dataset.add.label_strategy.exclude'), },
  ]

  const [form] = useForm()
  const [currentType, setCurrentType] = useState(TYPES.INTERNAL)
  const [publicDataset, setPublicDataset] = useState([])
  const [fileToken, setFileToken] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(id ? Number(id) : null)
  const [newKeywords, setNewKeywords] = useState([])
  const [ignoredKeywords, setIgnoredKeywords] = useState([])
  const [{ newer }, checkKeywords] = useAddKeywords(true)
  const [{ repeated: updatedRepeated }, updateKeywords] = useAddKeywords()
  const [addResult, newDataset] = useFetch('dataset/createDataset')

  useEffect(() => {
    form.setFieldsValue({ datasetId: null })
  }, [currentType])

  useEffect(async () => {
    if (!publicDataset.length) {
      const result = await props.getInternalDataset()
      if (result) {
        setPublicDataset(result.items)
      }
    }
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
    if (addResult) {
      message.success(t('dataset.add.success.msg'))
      props.clearCache()
      const group = addResult.dataset_group_id || ''
      history.replace(`/home/project/${pid}/dataset#${group}`)
    }
  }, [addResult])

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
    if (currentType === TYPES.LOCAL && !fileToken) {
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
      if (fileToken) {
        params.url = fileToken
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

  function onInternalDatasetChange(value) {
    setSelectedDataset(value)
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
        onClick={e => updateIgnoredKeywords(e, [key], !isIgnoreKeywords)}
        onClose={e => updateIgnoredKeywords(e, [key], isIgnoreKeywords)}
      >
        {key}
      </Tag>
    ) : t('common.empty.keywords')
  }

  function getSelectedDatasetKeywords() {
    const set = publicDataset.find(d => d.id === selectedDataset)
    return set?.keywords || []
  }

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
            <Form.Item
              label={t('dataset.add.form.name.label')}
              name='name'
              initialValue={'dataset_import_' + randomNumber()}
              rules={[
                { required: true, whitespace: true, message: t('dataset.add.form.name.required') },
                { type: 'string', min: 2, max: 80 },
              ]}
            >
              <Input autoComplete={'off'} allowClear />
            </Form.Item>
            <Form.Item label={t('dataset.add.form.type.label')}>
              <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.INTERNAL}>
                {types.map(type => (
                  <Option value={type.id} key={type.id}>{type.label}</Option>
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
                  <Select placeholder={t('dataset.add.form.internal.placeholder')} onChange={(value) => onInternalDatasetChange(value)}>
                    {publicDataset.map(dataset => (
                      <Option value={dataset.id} key={dataset.id}>{dataset.name} {dataset.versionName} (Total: {dataset.assetCount})</Option>
                    ))}
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
                <ProjectDatasetSelect pid={pid} placeholder={t('dataset.add.form.copy.placeholder')}></ProjectDatasetSelect>
              </Form.Item>
            ) : null}
            {!isType(TYPES.INTERNAL) ?
              <Form.Item label={t('dataset.add.form.label.label')} name='strategy' initialValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE}>
                <Radio.Group options={labelOptions.filter(option => !isType(TYPES.COPY) || option.value !== IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE)} />
              </Form.Item> : null}
            {isType(TYPES.NET) ? (
              <Form.Item label={t('dataset.add.form.net.label')} required>
                <Form.Item
                  name='url'
                  noStyle
                  rules={[
                    { required: true, message: t('dataset.add.form.net.tip') },
                    { validator: urlValidator, }
                  ]}
                >
                  <Input placeholder={t('dataset.add.form.net.tip')} max={512} allowClear />
                </Form.Item>
                <p>Sample: https://www.examples.com/pascal.zip</p>
              </Form.Item>
            ) : null}

            {isType(TYPES.PATH) ? (
              <Form.Item label={t('dataset.add.form.path.label')} required
                name='path'
                help={t('dataset.add.form.path.tip')}
                rules={[{ required: true, message: t('dataset.add.form.path.tip') }]}
              >
                <Input placeholder={t('dataset.add.form.path.placeholder')} max={512} allowClear />
              </Form.Item>
            ) : null}
            {isType(TYPES.LOCAL) ? (
              <Form.Item label={t('dataset.add.form.upload.btn')} required>
                <Uploader
                  onChange={(files, result) => { setFileToken(result) }}
                  max={1024}
                  onRemove={() => setFileToken('')}
                  info={t('dataset.add.form.upload.tip', {
                    br: <br />,
                    sample: <a target='_blank' href={'/sample_dataset.zip'}>Sample.zip</a>,
                    pic: <img src={samplePic} />
                  })}
                ></Uploader>
              </Form.Item>
            ) : null}
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
    </div>
  )
}


const actions = (dispatch) => {
  return {
    getInternalDataset: (payload) => {
      return dispatch({
        type: 'dataset/getInternalDataset',
        payload,
      })
    },
    createDataset: (payload) => {
      return dispatch({
        type: 'dataset/createDataset',
        payload,
      })
    },
    clearCache() {
      return dispatch({ type: "dataset/clearCache", })
    },
    updateKeywords: (payload) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload,
      })
    },
  }
}

export default connect(null, actions)(Add)
