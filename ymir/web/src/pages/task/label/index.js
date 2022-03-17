import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Input, Card, Button, Form, Row, Col, Checkbox, ConfigProvider, Space, Radio, Tag, } from "antd"
import styles from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"

import t from "@/utils/t"
import { useHistory, useParams, Link } from "umi"
import Uploader from "@/components/form/uploader"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"

const LabelTypes = () => [
  { id: "part", label: t('task.label.form.type.newer'), checked: true },
  { id: "all", label: t('task.label.form.type.all') },
]

function Label({ datasets, keywords, ...props }) {
  const pageParams = useParams()
  const id = Number(pageParams.id)
  const history = useHistory()
  const [dataset, setDataset] = useState({})
  const [doc, setDoc] = useState(undefined)
  const [form] = Form.useForm()
  const [asChecker, setAsChecker] = useState(false)


  useEffect(() => {
    id && props.getDataset(id)
  }, [id])

  useEffect(() => {
    props.getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    datasets[id] && setDataset(datasets[id])
  }, [datasets])

  useEffect(() => {
    const state = history.location.state

    if (state?.record) {
      const { parameters, name, } = state.record
      const { include_classes, include_datasets, labellers, extra_url, keep_annotations } = parameters

      const fvalue = {
        name: name.replace(/\w{6}$/, randomNumber()),
        labellers: labellers[0],
        keepAnnotations: keep_annotations,
        checker: labellers.length > 1 ? labellers[1] : '',
      }
      if (extra_url) {
        fvalue.desc = [{ uid: -1, status: 'done', name: extra_url.replace(/.*\/([^\/]+)$/, '$1'), url: extra_url }]
      }
      form.setFieldsValue(fvalue)
      setDoc(extra_url)
      setAsChecker(labellers.length > 1)

      history.replace({ state: {} })
    }
  }, [history.location.state])

  const onFinish = async (values) => {
    const { labellers, checker } = values
    const emails = [labellers]
    checker && emails.push(checker)
    const params = {
      ...values,
      projectId: dataset.projectId,
      datasetId: id,
      name: values.name.trim(),
      labellers: emails,
      doc,
    }
    const result = await props.createLabelTask(params)
    if (result) {
      await props.clearCache()
      history.replace(`/home/project/detail/${dataset.projectId}`)
    }
  }

  function docChange(files, docFile) {
    setDoc(files.length ? location.protocol + '//' + location.host + docFile : '')
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_label_' + randomNumber(),
    keep_annotations: true,
    labelType: getCheckedValue(LabelTypes()),
  }
  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.task.label')}>
        <div className={commonStyles.formContainer}>
          <Form
            className={styles.form}
            {...formLayout}
            form={form}
            name='labelForm'
            initialValues={initialValues}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            labelAlign={'left'}
            colon={false}
          >
            <Tip hidden={true}>
              <Form.Item label={t('task.fusion.form.dataset')}><span>{dataset.name} {dataset.versionName}</span></Form.Item>
            </Tip>
            <Tip hidden={true}>
              <Form.Item
                label={t('task.common.dataset.name')}
                name='name'
                rules={[
                  { required: true, whitespace: true, message: t('task.common.dataset.name.required') },
                  { type: 'string', min: 2, max: 50 },
                ]}
              >
                <Input placeholder={t('task.common.dataset.name.placeholder')} autoComplete='off' allowClear />
              </Form.Item>
            </Tip>
            <Tip content={t('tip.task.filter.labelmember')}>
              <Form.Item
                label={t('task.label.form.member')}
                required
              >
                <Row gutter={20}>
                  <Col flex={1}>
                    <Form.Item
                      name="labellers"
                      noStyle
                      rules={[
                        { required: true, message: t('task.label.form.member.required') },
                        { type: 'email', message: t('task.label.form.member.email.msg') },
                      ]}
                    >
                      <Input placeholder={t('task.label.form.member.placeholder')} allowClear />
                    </Form.Item>
                  </Col>
                  <Col style={{ lineHeight: '30px' }}>
                    <Checkbox checked={asChecker} onChange={({ target }) => setAsChecker(target.checked)}>{t('task.label.form.plat.checker')}</Checkbox>
                  </Col>
                </Row>
              </Form.Item>
            </Tip>

            <Tip hidden={!asChecker} content={t('tip.task.filter.labelplatacc')}>
              <Form.Item hidden={!asChecker} label={t('task.label.form.plat.label')} required>
                <Row gutter={20}>
                  <Col flex={1}>
                    <Form.Item
                      name="checker"
                      noStyle
                      rules={asChecker ? [
                        { required: true, message: t('task.label.form.member.required') },
                        { type: 'email', message: t('task.label.form.member.email.msg') },
                      ] : []}
                    >
                      <Input placeholder={t('task.label.form.member.labelplatacc')} allowClear />
                    </Form.Item>
                  </Col>
                  <Col>
                    <a target='_blank' href={'/label_tool/'}>{t('task.label.form.plat.go')}</a>
                  </Col>
                </Row>
              </Form.Item>
            </Tip>


            <Tip content={t('tip.task.filter.labeltarget')}>
              <Form.Item
                label={t('task.label.form.target.label')}
                name="keywords"
                rules={[
                  { required: true, message: t('task.label.form.target.placeholder') }
                ]}
              >
                <Select mode="multiple" showArrow
                  placeholder={t('task.label.form.member.labeltarget')}
                  filterOption={(value, option) => [option.value, ...(option.aliases || [])].some(key => key.indexOf(value) >= 0)}>
                  {keywords.map(keyword => (
                    <Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                      <Row>
                        <Col flex={1}>{keyword.name}</Col>
                      </Row>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Tip>
            <Tip hidden={true}>
              <Form.Item name='keepAnnotations'
                required
                label={t('task.label.form.keep_anno.label')}>
                <Radio.Group options={[
                  { value: true, label: t('common.yes') },
                  { value: false, label: t('common.no') },
                ]} />
              </Form.Item>
            </Tip>

            <Tip hidden={true}>
              <Form.Item label={t('task.label.form.desc.label')} name='desc'>
                <Uploader onChange={docChange} onRemove={() => setDoc(undefined)} format="doc"
                  max={50} info={t('task.label.form.desc.info', { br: <br /> })}></Uploader>
              </Form.Item>
            </Tip>
            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 8 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit">
                      {t('task.create')}
                    </Button>
                  </Form.Item>
                  <Form.Item name='backBtn' noStyle>
                    <Button size="large" onClick={() => history.goBack()}>
                      {t('task.btn.back')}
                    </Button>
                  </Form.Item>
                </Space>
                <div className={styles.bottomTip}>{t('task.label.bottomtip', { link: <Link target='_blank' to={'/label_tool/'}>{t('task.label.bottomtip.link.label')}</Link> })}</div>
              </Form.Item>
            </Tip>
          </Form>
        </div>
      </Card>
    </div>
  )
}

const dis = (dispatch) => {
  return {
    getDataset(id) {
      return dispatch({
        type: "dataset/getDataset",
        payload: id,
      })
    },
    createLabelTask(payload) {
      return dispatch({
        type: "task/createLabelTask",
        payload,
      })
    },
    clearCache() {
      return dispatch({ type: "dataset/clearCache", })
    },
    getKeywords(payload) {
      return dispatch({
        type: 'keyword/getKeywords',
        payload,
      })
    },
  }
}

const stat = (state) => {
  return {
    datasets: state.dataset.dataset,
    keywords: state.keyword.keywords.items,
  }
}

export default connect(stat, dis)(Label)
