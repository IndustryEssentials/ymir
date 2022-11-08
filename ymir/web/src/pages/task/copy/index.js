import React, { useState, useEffect } from "react"
import { connect } from "dva"
import { Input, Button, Form, message, Radio, Card, Space } from "antd"
import { useHistory, useLocation, useParams } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import { randomNumber } from "@/utils/number"
import Breadcrumbs from "@/components/common/breadcrumb"
import commonStyles from "../common.less"
import Desc from "@/components/form/desc"
import DatasetName from "@/components/form/items/datasetName"

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
      const group = result.dataset_group_id || ''
      history.replace(`/home/project/${pid}/dataset#${group}`)
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
          <Form.Item label={t('dataset.copy.form.dataset')}><span>{dataset.name} {dataset.versionName} (assets: {dataset.assetCount})</span></Form.Item>
          <DatasetName itemProps={{ initialValue: 'dataset_copy_' + randomNumber() }} />
          <Desc form={form} />
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
