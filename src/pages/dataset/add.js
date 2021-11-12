import { useEffect, useState } from 'react'
import { Button, Form, Input, message, Modal, Select, Space, Tag } from 'antd'
import { connect } from 'dva'

import s from './add.less'
import t from '@/utils/t'
import Uploader from '../../components/form/uploader'
import { randomNumber } from '../../utils/number'

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  INTERNAL: 1,
  SHARE: 2,
  NET: 3,
  LOCAL: 4,
  PATH: 5,
})


const Add = ({ id, visible, cancel = () => { }, ok = () => { }, getInternalDataset, createDataset }) => {

  const types = [
    { id: TYPES.INTERNAL, label: t('dataset.add.types.internal') },
    // { id: TYPES.SHARE, label: t('dataset.add.types.share') },
    { id: TYPES.NET, label: t('dataset.add.types.net') },
    { id: TYPES.LOCAL, label: t('dataset.add.types.local') },
    { id: TYPES.PATH, label: t('dataset.add.types.path') },
  ]
  const [form] = useForm()
  const [show, setShow] = useState(visible)
  const [currentType, setCurrentType] = useState(TYPES.INTERNAL)
  const [publicDataset, setPublicDataset] = useState([])
  const [selected, setSelected] = useState([])
  const [fileToken, setFileToken] = useState('')
  const [selectedDataset, setSelectedDataset] = useState(null)


  useEffect(async () => {
    form.resetFields()
    if (!visible) {
      initState()
    }
    if (visible && !publicDataset.length) {
      const result = await getInternalDataset()
      if (result) {
        setPublicDataset(result.items)
      }
    }
  }, [visible])

  useEffect(() => {
    setSelectedDataset(id ? Number(id) : null)
  }, [id])

  useEffect(() => {
    setShow(visible)
  }, [visible])

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

  const onOk = async () => {

    form.validateFields().then(submit).catch(errorInfo => { })
  }
  const onCancel = () => {
    close()
  }

  async function submit(values) {
    if (currentType === TYPES.LOCAL && !fileToken) {
      return message.error('Please upload local file')
    }
    var params = {
      ...values,
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

  return (
    <Modal
      visible={show}
      title={t('dataset.import.label')}
      onCancel={onCancel}
      onOk={onOk}
      destroyOnClose={true}
    >
      <Form form={form} labelCol={{ span: 4 }}>
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
            <Form.Item label={t('task.filter.form.include.label')}>
              {renderPublicKeywords()}
            </Form.Item>
            <Form.Item
              label={t('dataset.add.form.internal.label')}
              name='input_dataset_id'
              initialValue={selectedDataset}
              rules={isType(TYPES.INTERNAL) ? [
                { required: true, message: t('dataset.add.form.internal.required') }
              ] : []}
            >
              <Select placeholder={t('dataset.add.form.internal.placeholder')} onChange={(value) => setSelectedDataset(value)}>
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
              rules={[{ required: true, message: t('dataset.add.form.net.tip')}]}
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
              rules={[{ required: true, message: t('dataset.add.form.path.tip')}]}
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
      </Form>
    </Modal>
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
