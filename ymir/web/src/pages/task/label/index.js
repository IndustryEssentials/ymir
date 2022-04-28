import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Input, Card, Button, Form, Row, Col, Checkbox, ConfigProvider, Space, Radio, Tag, } from "antd"
import styles from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"

import t from "@/utils/t"
import { useHistory, useParams, Link, useLocation } from "umi"
import Uploader from "@/components/form/uploader"
import Breadcrumbs from "@/components/common/breadcrumb"
import { randomNumber } from "@/utils/number"
import Tip from "@/components/form/tip"
import DatasetSelect from "../../../components/form/datasetSelect"

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

  useEffect(() => {
    func.getKeywords({ limit: 100000 })
  }, [])

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
    const result = await func.createLabelTask(params)
    if (result) {
      if (iterationId) {
        func.updateIteration({ id: iterationId, currentStage, [outputKey]: result.result_dataset.id })
      }
      await func.clearCache()
      history.replace(`/home/project/detail/${pid}`)
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
    keepAnnotations: true,
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
              <Form.Item label={t('task.fusion.form.dataset')} name='datasetId'>
                <DatasetSelect pid={pid} />
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
                    <Select.Option key={keyword.name} value={keyword.name} aliases={keyword.aliases}>
                      <Row>
                        <Col flex={1}>{keyword.name}</Col>
                      </Row>
                    </Select.Option>
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
            </Tip>
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
