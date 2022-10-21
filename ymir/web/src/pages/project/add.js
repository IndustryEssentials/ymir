import { useEffect, useState } from 'react'
import { Button, Card, Form, Input, message, Modal, Select, Space, Radio, Row, Col } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory, useLocation } from "umi"

import s from './add.less'
import t from '@/utils/t'
import Breadcrumbs from '@/components/common/breadcrumb'
import DatasetSelect from '@/components/form/datasetSelect'
import Panel from '@/components/form/panel'
import useFetch from '@/hooks/useFetch'

const { useForm } = Form
const { confirm } = Modal

const Add = ({ keywords, datasets, getKeywords, ...func }) => {
  const { id } = useParams()
  const history = useHistory()
  const location = useLocation()
  const [form] = useForm()
  const [isEdit, setEdit] = useState(false)
  const [project, getProject] = useFetch('project/getProject', {})
  const [_, checkDuplication] = useFetch('keyword/checkDuplication')

  useEffect(() => {
    setEdit(!!id)

    id && getProject({ id })
  }, [id])

  useEffect(() => {
    getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    initForm(project)
  }, [project])

  function initForm(project = {}) {
    const { name, keywords: kws, trainSetVersion,
      description, enableIteration, testingSets } = project
    if (name) {
      form.setFieldsValue({
        name, keywords: kws, description,
        trainSetVersion,
        enableIteration,
        testingSets: testingSets.length ? testingSets : undefined,
      })
    }
  }

  const submit = async ({ name = '', description = '', ...values }) => {
    const action = isEdit ? 'update' : 'create'
    var params = {
      ...values,
    }
    if (isEdit) {
      params.id = id
    }
    params.name = (name || '').trim()
    params.description = (description || '').trim()

    if (isEdit && params.name === project.name) {
      delete params.name
    }

    const send = async () => {
      const result = await func[`${action}Project`](params)
      if (result) {
        const pid = result.id || id
        message.success(t(`project.${action}.success`))
        history.push(`/home/project/${pid}/detail`)
      }
    }
    // edit project
    if (isEdit) {
      return send()
    }
    // create project
    const kws = params.keywords.map(kw => (kw || '').trim()).filter(kw => kw)
    const { newer } = await checkDuplication(kws)

    if (newer?.length) {
      // confirm
      confirm({
        title: t('project.add.confirm.title'),
        content: <ol>{newer.map(keyword => <li key={keyword}>{keyword}</li>)}</ol>,
        onOk: () => {
          addNewKeywords(newer, send)
        },
        okText: t('project.add.confirm.ok'),
        cancelText: t('project.add.confirm.cancel'),
      })
    } else {
      send()
    }
  }


  const addNewKeywords = async (keywords, callback = () => { }) => {
    const result = func.addKeywords(keywords)
    if (result) {
      setTimeout(() => callback(), 500)
    }
  }

  function validateKeywords(_, kws) {
    if (kws?.length) {
      const valid = kws.every(kw => (kw || '').trim())
      if (!valid) {
        return Promise.reject(t('project.keywords.invalid'))
      }
    }
    return Promise.resolve()
  }

  const renderTitle = t(`breadcrumbs.project.${isEdit ? 'edit' : 'add'}`)

  return (
    <div className={s.projectAdd}>
      <Breadcrumbs />
      <Card className={s.container} title={renderTitle}>
        <div className={s.formContainer}>
          <Form form={form} labelCol={{ offset: 2, span: 6 }} wrapperCol={{ span: 12 }}
            colon={false} labelAlign='left' onFinish={submit} scrollToFirstError>
            <Panel hasHeader={false}>
              <Form.Item
                label={t('project.add.form.name')}
                name='name'
                rules={[
                  { required: true, whitespace: true, message: t('project.add.form.name.required') },
                  { min: 1, max: 100 },
                ]}
              >
                <Input placeholder={t('project.add.form.name.placeholder')} autoComplete='off' allowClear />
              </Form.Item>
              <Form.Item
                label={t('project.add.form.type')}
                name='type'
                initialValue={0}
              >
                <Radio.Group>
                  <Radio value={0}>{t('task.train.form.traintypes.detect')}</Radio>
                </Radio.Group>
              </Form.Item>
              <Form.Item
                label={t('project.train_classes')}
                name="keywords"
                rules={[
                  { required: true, message: t('project.add.form.keyword.required') },
                  { validator: validateKeywords },
                ]}
                tooltip={t('project.add.form.keyword.tip')}
              >
                <Select mode="tags" showArrow tokenSeparators={[',']}
                  placeholder={t('project.add.form.keyword.placeholder')}
                  disabled={isEdit && project?.currentIteration?.id}
                  filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                  {keywords.map(keyword => (
                    <Select.Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                      <Row>
                        <Col flex={1}>{keyword.name}</Col>
                      </Row>
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                label={t('project.add.form.enableIteration')}
                name='enableIteration'
                hidden={true}
                initialValue={true}
                required
                tooltip={t('project.add.form.enableIteration.tip')}
              >
                <Radio.Group disabled={isEdit} options={[
                  { value: true, label: t('common.yes') },
                  { value: false, label: t('common.no') },
                ]} />
              </Form.Item>
              {isEdit ?
                <Form.Item label={t('project.add.form.testing.set')} name="testingSets" tooltip={t('project.add.form.testingset.tip')}>
                  <DatasetSelect
                    pid={id}
                    mode='multiple'
                    filters={useCallback(datasets => datasets.filter(ds => ds.keywordCount > 0 && ds.groupId !== project?.trainSet?.id), [project?.trainSet?.id])}
                    allowClear
                  />
                </Form.Item> : null}
              <Form.Item label={t('project.add.form.desc')} name='description'
                rules={[
                  { max: 500 },
                ]}
              >
                <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
              </Form.Item>
            </Panel>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {isEdit ? t('common.confirm') : t('project.add.submit')}
                  </Button>
                </Form.Item>
                <Form.Item name='backBtn' noStyle>
                  <Button size="large" onClick={() => history.goBack()}>
                    {t('common.back')}
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

const props = (state) => {
  return {
    keywords: state.keyword.keywords.items,
    datasets: state.project.datasets,
  }
}

const actions = (dispatch) => {
  const updateKeywords = (dry_run = false) => {
    return (keywords) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload: {
          keywords: keywords.map(keyword => ({ name: keyword, aliases: [] })),
          dry_run,
        },
      })
    }
  }
  return {
    createProject: (payload) => {
      return dispatch({
        type: 'project/createProject',
        payload,
      })
    },
    updateProject: (payload) => {
      return dispatch({
        type: 'project/updateProject',
        payload,
      })
    },
    getKeywords(payload) {
      return dispatch({
        type: 'keyword/getKeywords',
        payload,
      })
    },
    checkKeywords: updateKeywords(true),
    addKeywords: updateKeywords(),
  }
}

export default connect(props, actions)(Add)
