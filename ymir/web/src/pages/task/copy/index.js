import React, { useState, useEffect } from "react"
import { connect } from "dva"
import { Input, Button, Form, message, Radio, Card, Space } from "antd"
import { useHistory, useLocation, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { randomNumber } from "@/utils/number"
import Breadcrumbs from "@/components/common/breadcrumb"
import commonStyles from "../common.less"
import Tip from "@/components/form/tip"

function Copy({ allDatasets, datasetCache, ...props }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { did } = location.query
  const [form] = Form.useForm()
  const [dataset, setDataset] = useState({})

  useEffect(() => {
    pid && props.getDatasets(pid)
  }, [pid])

  useEffect(() => {
    did && props.getDataset(did)
  }, [did])

  useEffect(() => {
    const dst = datasetCache[did]
    dst && setDataset(dst)
  }, [datasetCache])

  const onFinish = async (values) => {
    const params = {
      ...values,
      projectId: pid,
      datasetId: did,
    }
    const result = await props.createDataset(params)
    if (result) {
      message.success(t('dataset.copy.success.msg'))
      props.clearCache()
      history.replace(`/home/project/detail/${pid}`)
    }
  }

  const onFinishFailed = (err) => {
    console.log("on finish failed: ", err)
  }

  return (
    <div className={commonStyles.wrapper}>
      <Breadcrumbs />
      <Card className={commonStyles.container} title={t('breadcrumbs.datasets.copy')}>
        <Form
          form={form}
          name='fusionForm'
          {...formLayout}
          onFinish={onFinish}
          onFinishFailed={onFinishFailed}
          labelAlign={'left'}
          colon={false}
        >
          <Tip hidden={true}>
            <Form.Item label={t('dataset.copy.form.dataset')}><span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span></Form.Item>
          </Tip>
          <Tip hidden={true}>
            <Form.Item
              label={t('dataset.add.form.name.label')}
              name='name'
              initialValue={'dataset_copy_' + randomNumber()}
              rules={[
                { required: true, whitespace: true, message: t('dataset.add.form.name.required') },
                { type: 'string', min: 2, max: 80 },
              ]}
            >
              <Input autoComplete={'off'} allowClear />
            </Form.Item>
          </Tip>
          <Tip hidden={true}>
            <Form.Item label={t('dataset.copy.form.desc.label')} name='description'
              rules={[
                { max: 100 },
              ]}
            >
              <Input.TextArea autoSize={{ minRows: 4, maxRows: 20 }} />
            </Form.Item>
          </Tip>
          <Tip hidden={true}>
            <Form.Item wrapperCol={{ offset: 8 }}>
              <Space size={20}>
                <Form.Item name='submitBtn' noStyle>
                  <Button type="primary" size="large" htmlType="submit">
                    {t('common.action.copy')}
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
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    allDatasets: state.dataset.allDatasets,
    datasetCache: state.dataset.dataset,
  }
}
const mapDispatchToProps = (dispatch) => {
  return {
    getDatasets(pid) {
      return dispatch({
        type: "dataset/queryAllDatasets",
        payload: { pid, force: true },
      })
    },
    getDataset(id, force) {
      return dispatch({
        type: "dataset/getDataset",
        payload: { id, force },
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
  }
}

export default connect(props, mapDispatchToProps)(Copy)
