import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Input, Card, Button, Form, Row, Col, Checkbox, Space, Radio, } from "antd"
import { useHistory, useParams, Link, useLocation } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import Uploader from "@/components/form/uploader"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber } from "@/utils/number"
import useFetch from '@/hooks/useFetch'

import DatasetSelect from "../../../components/form/datasetSelect"
import Desc from "@/components/form/desc"
import Tip from "@/components/form/tip"

import styles from "./index.less"
import commonStyles from "../common.less"
import KeepAnnotations from "./components/keepAnnotations"

const LabelTypes = () => [
  { id: "part", label: t('task.label.form.type.newer'), checked: true },
  { id: "all", label: t('task.label.form.type.all') },
]

function Label({ datasets, keywords, ...func }) {
  const pageParams = useParams()
  const { query } = useLocation()
  const pid = Number(pageParams.id)
  const { iterationId, outputKey, currentStage } = query
  const did = Number(query.did)
  const history = useHistory()
  const [doc, setDoc] = useState(undefined)
  const [form] = Form.useForm()
  const [asChecker, setAsChecker] = useState(false)
  const [project, getProject] = useFetch('project/getProject', {})

  useEffect(() => {
    func.getKeywords({ limit: 100000 })
  }, [])

  useEffect(() => {
    iterationId && pid && getProject({ id: pid })
  }, [pid, iterationId])

  useEffect(() => {
    project.id && form.setFieldsValue({ keywords: project.keywords})
  }, [project])

  const onFinish = async (values) => {
    const { labellers, checker } = values
    const emails = [labellers]
    checker && emails.push(checker)
    const params = {
      ...values,
      projectId: pid,
      labellers: emails,
      doc,
      name: 'task_label_' + randomNumber(),
    }
    const result = await func.label(params)
    if (result) {
      if (iterationId) {
        func.updateIteration({ id: iterationId, currentStage, [outputKey]: result.result_dataset.id })
      }
      await func.clearCache()
      const group = result.result_dataset?.dataset_group_id || ''
      let redirect = `/home/project/${pid}/dataset#${group}`
      if (iterationId) {
        redirect = `/home/project/${pid}/iterations`
      }
      history.replace(redirect)
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
    datasetId: did || undefined,
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
          >
            <Form.Item wrapperCol={{ span: 20 }}><Tip content={t('task.label.header.tip')} /></Form.Item>
            <Form.Item label={t('task.fusion.form.dataset')} name='datasetId'>
              <DatasetSelect pid={pid} />
            </Form.Item>
            {false ? <Form.Item
              label={t('task.label.form.member')}
              tooltip={t('tip.task.filter.labelmember')}
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
            </Form.Item> : null }
            <Form.Item hidden={!asChecker}
              tooltip={t('tip.task.filter.labelplatacc')}
              label={t('task.label.form.plat.label')} required>
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
            <Form.Item
              label={t('task.label.form.target.label')}
              tooltip={t('tip.task.filter.labeltarget')}
              name="keywords"
              rules={[
                { required: true, message: t('task.label.form.target.placeholder') }
              ]}
            >
              <Select mode="multiple" showArrow
                placeholder={t('task.label.form.member.labeltarget')}
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
            <KeepAnnotations />
            <Form.Item label={t('task.label.form.desc.label')} name='desc'>
              <Uploader onChange={docChange} onRemove={() => setDoc(undefined)} format="doc"
                max={50} info={t('task.label.form.desc.info', { br: <br /> })}></Uploader>
            </Form.Item>
            <Desc form={form} />
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.label')}
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
          </Form>
        </div>
      </Card>
    </div>
  )
}

const dis = (dispatch) => {
  return {
    getDataset(id, force) {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
      })
    },
    label(payload) {
      return dispatch({
        type: "task/label",
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
    updateIteration(params) {
      return dispatch({
        type: 'iteration/updateIteration',
        payload: params,
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
