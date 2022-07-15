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
import { getKeywords } from '../../services/keyword'
import Tip from "@/components/form/tip"
import ProjectDatasetSelect from '../../components/form/projectDatasetSelect'
import useAddKeywords from '@/hooks/useAddKeywords'
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
    { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: t('dataset.add.label_strategy.include'), },
    { value: IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE, label: t('dataset.add.label_strategy.exclude'), },
  ]
  const labelStrategyOptions = [
    { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE, label: t('dataset.add.label_strategy.ignore'), },
    { value: 0, label: t('dataset.add.label_strategy.add'), },
    { value: IMPORTSTRATEGY.UNKOWN_KEYWORDS_STOP, label: t('dataset.add.label_strategy.stop'), },
  ]
  const [form] = useForm()
  const [currentType, setCurrentType] = useState(TYPES.INTERNAL)
  const [publicDataset, setPublicDataset] = useState([])
  const [fileToken, setFileToken] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(id ? Number(id) : null)
  const [showLabelStrategy, setShowLS] = useState(true)
  const [strategy, setStrategy] = useState(IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)
  const [kStrategy, setKStrategy] = useState(0)
  const [newKeywords, setNewKeywords] = useState([])
  const [{ newer }, checkKeywords] = useAddKeywords(true)


  useEffect(async () => {
    if (!publicDataset.length) {
      const result = await props.getInternalDataset()
      if (result) {
        setPublicDataset(result.items)
      }
    }
  }, [])

  useEffect(() => {
    const ds = publicDataset.find(set => set.id === selectedDataset)
    if (ds) {
      setNewKeywords(ds.keywords)
    }
  }, [selectedDataset])

  useEffect(() => {
    setStrategy(kStrategy || IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)
    if (!kStrategy) {
      renderKeywords()
    }
  }, [kStrategy])

  useEffect(() => {
    renderKeywords()
  }, [selectedDataset])

  useEffect(() => {
    if (newer.length) {
      const unique = newer.map(k => ({ name: k, type: 0 }))
      setNewKeywords(unique)
      form.setFieldsValue({ new_keywords: unique })
    }
  }, [newer])

  const typeChange = (type) => {
    setCurrentType(type)
    form.setFieldsValue({
      with_annotations: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE,
      k_strategy: IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE,
    })
    setShowLS(true)
    setKStrategy(IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)
  }

  const isType = (type) => {
    return currentType === type
  }

  async function submit(values) {
    if (currentType === TYPES.LOCAL && !fileToken) {
      return message.error(t('dataset.add.local.file.empty'))
    }
    const kws = form.getFieldValue('new_keywords')
    if (kws && kws.length && !kStrategy && isType(TYPES.INTERNAL)) {
      const addKwParams = kws.filter(k => k.type === 0).map(k => ({ name: k.name }))
      const kResult = await props.updateKeywords({ keywords: addKwParams })
      if (!kResult) {
        return message.error(t('keyword.add.failure'))
      }
    }
    let params = {
      ...values,
      strategy,
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
    const result = await props.createDataset(params)
    if (result) {
      message.success(t('dataset.add.success.msg'))
      props.clearCache()
      history.push(`/home/project/${pid}/dataset`)
    }
  }

  function onFinishFailed(err) {
    console.log('finish failed: ', err)
  }

  function strategyFilter() {
    return labelStrategyOptions.filter(option =>
      isType(TYPES.INTERNAL) ?
        option.value !== IMPORTSTRATEGY.UNKOWN_KEYWORDS_STOP :
        option.value
    )
  }

  function onLabelChange({ target }) {
    setShowLS(target.value === IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE)
    setStrategy(target.value)
  }

  function onStrategyChange({ target }) {
    setKStrategy(target.value)
  }

  async function renderKeywords() {
    const kws = getSelectedDatasetKeywords()
    await checkKeywords(kws)
  }

  function onInternalDatasetChange(value) {
    setSelectedDataset(value)
  }

  function renderSelectedKeywords() {
    const kws = getSelectedDatasetKeywords()
    return kws.length ? kws.map(key => <Tag className={s.selectedTag} key={key}>{key}</Tag>) : t('common.empty.keywords')
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
            // initialValues={initialValues}
            onFinish={submit}
            onFinishFailed={onFinishFailed}
            labelAlign={'left'}
            colon={false}
          >
            <Tip hidden={true}>
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
            </Tip>

            <Tip hidden={true}>
              <Form.Item label={t('dataset.add.form.type.label')}>
                <Select onChange={(value) => typeChange(value)} defaultValue={TYPES.INTERNAL}>
                  {types.map(type => (
                    <Option value={type.id} key={type.id}>{type.label}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Tip>

            {isType(TYPES.INTERNAL) ? (
              <>
                <Tip content={t('tip.task.filter.datasets')}>
                  <Form.Item
                    label={t('dataset.add.form.internal.label')}
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
                </Tip>

                {selectedDataset ?
                  <Tip hidden={true}>
                    <Form.Item label={t('dataset.import.public.include')}>
                      {renderSelectedKeywords()}
                    </Form.Item>
                  </Tip>
                  : null}
              </>
            ) : null}
            {isType(TYPES.COPY) ? (
              <Tip hidden={true}>
                <Form.Item
                  label={t('dataset.add.form.copy.label')}
                  name='datasetId'
                  rules={[
                    { required: true, message: t('dataset.add.form.copy.required') }
                  ]}
                >
                  <ProjectDatasetSelect pid={pid} placeholder={t('dataset.add.form.copy.placeholder')}></ProjectDatasetSelect>
                </Form.Item>
              </Tip>
            ) : null}
            <Tip hidden={true}>
              <Form.Item label={t('dataset.add.form.label.label')} name='with_annotations' initialValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE}>
                <Radio.Group
                  options={labelOptions.filter(option => !isType(TYPES.INTERNAL) || option.value !== IMPORTSTRATEGY.ALL_KEYWORDS_IGNORE)}
                  onChange={onLabelChange}
                />
              </Form.Item>
            </Tip>
            {!isType(TYPES.COPY) ? <>
              {showLabelStrategy ?
                <Tip hidden={true}>
                  <Form.Item label={t('dataset.add.form.newkw.label')}>
                    <p className={s.newkwTip}><TipsIcon className={s.tipIcon} /> {t('dataset.add.form.newkw.tip')}</p>
                    <Row><Col flex={1}><Form.Item noStyle name='k_strategy' initialValue={IMPORTSTRATEGY.UNKOWN_KEYWORDS_IGNORE}>
                      <Radio.Group key={!isType(TYPES.INTERNAL) ? 'internal' : 'other'}
                        options={strategyFilter()}
                        onChange={onStrategyChange} />
                    </Form.Item></Col>
                      <Col><Link to={'/home/keyword'} target='_blank'>{t('dataset.add.form.newkw.link')}</Link></Col>
                    </Row>
                  </Form.Item>
                </Tip> : null}

              <Tip hidden={true}>
                <Form.Item hidden={kStrategy} wrapperCol={{ offset: 8, span: 16 }}>
                  {newKeywords.length > 0 ?
                    <Form.List name='new_keywords'>
                      {(fields, { add, remove }) => (

                        <Row>
                          {fields.map((field, index) => (
                            <Col span={12} className={s.odd}>
                              <Row gutter={22}>
                                <Col span={5} className={s.name}>{newKeywords[field.name]?.name}</Col>
                                <Col span={12}>
                                  <Form.Item
                                    {...field}
                                    name={[field.name, 'type']}
                                    fieldKey={[field.fieldKey, 'type']}
                                    initialValue={0}
                                    style={{ width: 150, display: 'inline-block' }}
                                  >
                                    <Select>
                                      <Select.Option value={0}>{t('dataset.add.newkw.asname')}</Select.Option>
                                      {/* <Select.Option value={1}>{t('dataset.add.newkw.asalias')}</Select.Option> */}
                                      <Select.Option value={2}>{t('dataset.add.newkw.ignore')}</Select.Option>
                                    </Select>
                                  </Form.Item>
                                </Col>
                              </Row>
                            </Col>
                          ))}
                        </Row>

                      )}
                    </Form.List>
                    : t('dataset.add.newkeyword.empty')}
                </Form.Item>
              </Tip> </> : null}
            {isType(TYPES.NET) ? (
              <Tip hidden={true}>
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
              </Tip>
            ) : null}

            {isType(TYPES.PATH) ? (
              <Tip hidden={true}>
                <Form.Item label={t('dataset.add.form.path.label')} required
                  name='path'
                  help={t('dataset.add.form.path.tip')}
                  rules={[{ required: true, message: t('dataset.add.form.path.tip') }]}
                >
                  <Input placeholder={t('dataset.add.form.path.placeholder')} max={512} allowClear />
                </Form.Item>
              </Tip>
            ) : null}
            {isType(TYPES.LOCAL) ? (
              <Tip hidden={true}>
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
              </Tip>
            ) : null}
            <Tip hidden={true}>
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
            </Tip>
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
