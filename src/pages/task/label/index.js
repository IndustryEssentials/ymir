import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Select, Input, Card, Button, Form, Row, Col, Checkbox, ConfigProvider, Space, Radio, } from "antd"
import styles from "./index.less"
import commonStyles from "../common.less"
import { formLayout } from "@/config/antd"

import t from "@/utils/t"
import { useHistory, useParams, Link } from "umi"
import Uploader from "../../../components/form/uploader"
import Breadcrumbs from "../../../components/common/breadcrumb"
import EmptyState from '@/components/empty/dataset'
import { randomNumber } from "../../../utils/number"

const { Option } = Select

const LabelTypes = () => [
  { id: "part", label: t('task.label.form.type.newer'), checked: true },
  { id: "all", label: t('task.label.form.type.all') },
]

function Label({ getDatasets, keywords, createLabelTask, getKeywords }) {
  const { id } = useParams()
  const datasetId = Number(id) || undefined
  const history = useHistory()
  const [datasets, setDatasets] = useState([])
  const [doc, setDoc] = useState(undefined)
  const [form] = Form.useForm()
  const [asChecker, setAsChecker] = useState(false)


  useEffect(async () => {
    let result = await getDatasets({ limit: 100000 })
    if (result) {
      setDatasets(result.items)
    }
  }, [])

  useEffect(() => {
    getKeywords()
  }, [])

  const onFinish = async (values) => {
    const { label_members, checker } = values
    const emails = [label_members]
    checker && emails.push(checker)
    const params = {
      ...values,
      name: values.name.trim(),
      label_members: emails,
      doc,
    }
    const result = await createLabelTask(params)
    if (result) {
      history.replace("/home/task")
    }
  }

  function onFinishFailed(errorInfo) {
    console.log("Failed:", errorInfo)
  }

  const getCheckedValue = (list) => list.find((item) => item.checked)["id"]
  const initialValues = {
    name: 'task_label_' + randomNumber(),
    datasets: datasetId,
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
            size='large'
            colon={false}
          >
            <Form.Item
              label={t('task.filter.form.name.label')}
              name='name'
              rules={[
                { required: true, whitespace: true, message: t('task.filter.form.name.placeholder') },
                { type: 'string', min: 2, max: 20 },
              ]}
            >
              <Input placeholder={t('task.filter.form.name.required')} autoComplete='off' allowClear />
            </Form.Item>
            <ConfigProvider renderEmpty={() => <EmptyState add={() => history.push('/home/dataset/add')} />}>
              <Form.Item
                label={t('task.filter.form.datasets.label')}
                name="datasets"
                rules={[
                  { required: true, message: t('task.filter.form.datasets.required') },
                ]}
              >
                <Select
                  placeholder={t('task.filter.form.datasets.placeholder')}
                  filterOption={(input, option) => option.key.toLowerCase().indexOf(input.toLowerCase()) >= 0}
                >
                  {datasets.map(item => (
                    <Option value={item.id} key={item.name}>
                      {item.name}({item.asset_count})
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </ConfigProvider>
            <Form.Item
              label={t('task.label.form.member')}
              required
            >
              <Row gutter={20}>
                <Col flex={1}>
                  <Form.Item
                    name="label_members"
                    noStyle
                    rules={[
                      { required: true, message: t('task.label.form.member.required') },
                      { type: 'email', message: t('task.label.form.member.email.msg') },
                    ]}
                  >
                    <Input placeholder={t('task.label.form.member.placeholder')} allowClear />
                  </Form.Item>
                </Col>
                <Col>
                  <Checkbox onChange={({ target }) => setAsChecker(target.checked)}>{t('task.label.form.plat.checker')}</Checkbox>
                </Col>
              </Row>
            </Form.Item>
            <Form.Item hidden={!asChecker} label={t('task.label.form.plat.label')} required>
              <Row gutter={20}>
                <Col flex={1}>
                  <Form.Item
                    name="checker"
                    noStyle
                    rules={[
                      { required: asChecker, message: t('task.label.form.member.required') },
                      { type: 'email', message: t('task.label.form.member.email.msg') },
                    ]}
                  >
                    <Input allowClear />
                  </Form.Item>
                </Col>
                <Col>
                  <a target='_blank' href={'/lsf/'}>{t('task.label.form.plat.go')}</a>
                </Col>
              </Row>
            </Form.Item>

            <Form.Item
              label={t('task.label.form.target.label')}
              name="keywords"
              rules={[
                { required: true, message: t('task.label.form.target.placeholder') }
              ]}
            >
              <Select mode="multiple" showArrow>
                {keywords.map(keyword => (
                  <Option key={keyword} value={keyword}>
                    {keyword}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            {/* next version */}
            {/* <Form.Item
              label={t('task.label.form.label.label')}
              name='with_labels'
            >
              <Radio.Group options={[
                { value: 1, label: t('task.mining.form.label.yes')},
                {value: 0, label: t('task.mining.form.label.no')}, 
              ]} defaultValue={0} />
            </Form.Item> */}
            <Form.Item label={t('task.label.form.desc.label')}>
              <Uploader onChange={(result) => { setDoc(result) }} format="doc" max={50} info={t('task.label.form.desc.info', { br: <br /> })}></Uploader>
            </Form.Item>
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
              <div className={styles.bottomTip}>{t('task.label.bottomtip', { link: <Link target='_blank' to={'/lsf/'}>{t('task.label.bottomtip.link.label')}</Link> })}</div>
            </Form.Item>
          </Form>
        </div>
      </Card>
    </div>
  )
}

const dis = (dispatch) => {
  return {
    getDatasets(payload) {
      return dispatch({
        type: "dataset/getDatasets",
        payload,
      })
    },
    createLabelTask(payload) {
      return dispatch({
        type: "task/createLabelTask",
        payload,
      })
    },
    getKeywords(payload) {
      return dispatch({
        type: 'common/getKeywords',
        payload,
      })
    },
  }
}

const stat = (state) => {
  return {
    keywords: state.common.keywords,
  }
}

export default connect(stat, dis)(Label)
