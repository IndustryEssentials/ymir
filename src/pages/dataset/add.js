import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Radio, Row, Col, Select, Space, Tag } from 'antd'
import { connect } from 'dva'
import { Link, useParams } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import Uploader from '../../components/form/uploader'
import { randomNumber } from '../../utils/number'
import s from './add.less'
import Breadcrumbs from '../../components/common/breadcrumb'
import { TipsIcon } from '../../components/common/icons'
import options from '@antv/graphin/lib/layout/utils/options'

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  INTERNAL: 1,
  SHARE: 2,
  NET: 3,
  LOCAL: 4,
  PATH: 5,
})


const Add = ({ cancel = () => { }, ok = () => { }, getInternalDataset, createDataset }) => {
  const { id } = useParams()
  const types = [
    { id: TYPES.INTERNAL, label: t('dataset.add.types.internal') },
    // { id: TYPES.SHARE, label: t('dataset.add.types.share') },
    { id: TYPES.NET, label: t('dataset.add.types.net') },
    { id: TYPES.LOCAL, label: t('dataset.add.types.local') },
    { id: TYPES.PATH, label: t('dataset.add.types.path') },
  ]
  const labelOptions = [
    { value: 0, label: t('dataset.add.label_strategy.include'), },
    { value: 1, label: t('dataset.add.label_strategy.exclude'), },
  ]
  const labelStrategyOptions = [
    { value: 0, label: t('dataset.add.label_strategy.ignore'), },
    { value: 1, label: t('dataset.add.label_strategy.add'), },
    { value: 2, label: t('dataset.add.label_strategy.stop'), },
  ]
  const [form] = useForm()
  const [currentType, setCurrentType] = useState(TYPES.INTERNAL)
  const [publicDataset, setPublicDataset] = useState([])
  const [selected, setSelected] = useState([])
  const [fileToken, setFileToken] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(id ? Number(id) : null)
  const [showLabelStrategy, setShowLS] = useState(true)
  const [strategy, setStrategy] = useState(2)
  const [newKeywords, setNewKeywords] = useState(
    [
      // { key: 'cat' }, { key: 'dog' }, { key: 'person' }
  ]
    )


  useEffect(async () => {
    // form.resetFields()
    // initState()
    if (!publicDataset.length) {
      const result = await getInternalDataset()
      console.log('get public dataset: ', result)
      if (result) {
        setPublicDataset(result.items)
      }
    }
  }, [])
  
  useEffect(() => {
    const ds = publicDataset.find(set => set.id === selectedDataset)
    if (ds) {
      // const result = getKeywords()

      setNewKeywords(ds.keywords)
    }
  }, [selectedDataset])

  const typeChange = (type) => {
    setCurrentType(type)
  }

  const isType = (type) => {
    return currentType === type
  }

  const close = () => {
    setShow(false)
    cancel()
  }

  async function submit(values) {
    if (currentType === TYPES.LOCAL && !fileToken) {
      return message.error('Please upload local file')
    }
    var params = {
      ...values,
      strategy,
    }
    if (currentType === TYPES.LOCAL && fileToken) {
      params.input_url = fileToken
    }
    const result = await createDataset(params)
    if (result) {
      message.success(t('dataset.add.success.msg'))
      form.resetFields()
      close()
      ok()
    }
  }

  function onFinishFailed(err) {
    console.log('finish failed: ', err)
  }

  function onLabelChange({ target }) {
    setShowLS(target.value === labelOptions[0].value)
    setStrategy(target.value === labelOptions[0].value ? 2 : 1)
  }

  function onStrategyChange({ target }) {
    setStrategy(target.value === labelStrategyOptions[2].value ? 3 : 2)
  }

  function onInternalDatasetChange(value) {
    setSelectedDataset(value)
  }

  function initState() {
    setCurrentType(TYPES.INTERNAL)
    setSelected([])
    setFileToken('')
    setSelectedDataset(null)
  }

  function renderPublicKeywords() {
    const keywords = publicDataset.reduce((prev, curr) => {
      return prev.concat(curr.keywords)
    }, [])


    return (<Select
      mode='multiple'
      onChange={(value) => currentKeyword(value)}
    >
      {[...new Set(keywords)].sort().map(keyword =>
        <Select.Option key={keyword} value={keyword}>{keyword}</Select.Option>
      )}
    </Select>)
  }

  function renderSelectedKeywords() {
    const set = publicDataset.find(d => d.id === selectedDataset)
    return set && set.keywords.length ? set.keywords.map(key => <Tag className={s.selectedTag} key={key}>{key}</Tag>) : t('common.empty.keywords')
  }

  function currentKeyword(values) {
    setSelected(values)
  }

  function filterDataset() {
    return selected.length ? publicDataset.filter(dataset => {
      return dataset.keywords.some((key) => selected.indexOf(key) > -1)
    }) : publicDataset
  }

  const addKwOptions = [
    { value: 0, label: t('dataset.add.newkw.asname'), },
    { value: 1, label: <>{t('dataset.add.newkw.asalias')}</>, },
    { value: 2, label: t('dataset.add.newkw.ignore'), },
  ]

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
            size='large'
            colon={false}
          >
            <Form.Item
              label={t('dataset.add.form.name.label')}
              name='name'
              initialValue={'dataset_import_' + randomNumber()}
              rules={[
                { required: true, whitespace: true, message: t('dataset.add.form.name.required') },
                { type: 'string', min: 2, max: 30 },
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
                  name='input_dataset_id'
                  initialValue={selectedDataset}
                  rules={isType(TYPES.INTERNAL) ? [
                    { required: true, message: t('dataset.add.form.internal.required') }
                  ] : []}
                >
                  <Select placeholder={t('dataset.add.form.internal.placeholder')} onChange={(value) => onInternalDatasetChange(value)}>
                    {filterDataset().map(dataset => (
                      <Option value={dataset.id} key={dataset.id}>{dataset.name} (Total: {dataset.asset_count})</Option>
                    ))}
                  </Select>
                </Form.Item>
                {selectedDataset ?
                  <Form.Item label={t('dataset.import.public.include')}>
                    {renderSelectedKeywords()}
                  </Form.Item>
                  : null}
              </>
            ) : null}
            <Form.Item label={t('dataset.add.form.label.label')}>
              <Radio.Group options={labelOptions} onChange={onLabelChange} defaultValue={labelOptions[0].value} />
            </Form.Item>
            {showLabelStrategy ?
              <Form.Item label={t('dataset.add.form.newkw.label')}>
                <p className={s.newkwTip}><TipsIcon className={s.tipIcon} /> {t('dataset.add.form.newkw.tip')}</p>
                <Row><Col flex={1}><Form.Item noStyle>
                  <Radio.Group key={!isType(TYPES.INTERNAL) ? 'internal' : 'other'}
                    options={labelStrategyOptions.filter(option => isType(TYPES.INTERNAL) ? true : option.value !== 1)}
                    onChange={onStrategyChange} defaultValue={labelOptions[0].value} />
                </Form.Item></Col>
                  <Col><Link to={'/home/keyword'} target='_blank'>{t('dataset.add.form.newkw.link')}</Link></Col>
                </Row>
              </Form.Item> : null}
            <Form.Item hidden={true} label={t('dataset.add.form.newkws.label')}>
            <Form.List name='hyperparam' initialValue={newKeywords}>
                {(fields, { add, remove }) => (
                  <>
                    {fields.map(field => (
                      <Row key={field.key} gutter={20}>
                        <Col flex={1}>{newKeywords[field.name].key}</Col>
                        {console.log('get field: ', field)}
                        <Col>
                          <Form.Item
                            {...field}
                            // label="Key"
                            name={[field.name, 'key']}
                            fieldKey={[field.fieldKey, 'key']}
                          >
                            <Radio.Group options={addKwOptions} defaultValue={0} />
                          </Form.Item>
                        </Col>
                      </Row>
                    ))}
                  </>
                )}
              </Form.List>
            </Form.Item>
            {isType(TYPES.SHARE) ? (
              <Form.Item
                label={t('dataset.add.form.share.label')}
                name='input_dataset_id'
                rules={[
                  { required: true, message: t('dataset.add.form.share.required') }
                ]}
              >
                <Input placeholder={t('dataset.add.form.share.placeholder')} allowClear />
              </Form.Item>
            ) : null}
            {isType(TYPES.NET) ? (
              <Form.Item label={t('dataset.add.form.net.label')} required>
                <Form.Item
                  name='input_url'
                  noStyle
                  rules={[
                    { required: true, message: t('dataset.add.form.net.tip') },
                    { type: 'url', }
                  ]}
                >
                  <Input placeholder={t('dataset.add.form.net.tip')} max={512} allowClear />
                </Form.Item>
                <p>Sample: https://www.examples.com/pascal.zip</p>
              </Form.Item>
            ) : null}
            {isType(TYPES.PATH) ? (
              <Form.Item label={t('dataset.add.form.path.label')} required>
                <Form.Item
                  name='input_path'
                  noStyle
                  rules={[{ required: true, message: t('dataset.add.form.path.tip') }]}
                >
                  <Input placeholder={t('dataset.add.form.path.placeholder')} max={512} allowClear />
                </Form.Item>
                <p>{t('dataset.add.form.path.tip')}</p>
              </Form.Item>
            ) : null}
            {isType(TYPES.LOCAL) ? (
              <Form.Item label={t('dataset.add.form.upload.btn')}>
                <Uploader
                  onChange={(result) => { setFileToken(result) }}
                  max={1024}
                  info={t('dataset.add.form.upload.tip', { br: <br />, sample: <a target='_blank' href={'/sample_dataset.zip'}>Sample.zip</a> })}
                ></Uploader>
              </Form.Item>
            ) : null}
            <Form.Item wrapperCol={{ offset: 4 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('task.filter.create')}
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
  }
}

export default connect(null, actions)(Add)
