import React, { useState, useEffect } from "react"
import { connect } from "dva"
import { Input, Button, Form, message, Radio, Card, Space } from "antd"
import { useHistory, useLocation, useParams, useSelector } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import useFetch from '@/hooks/useFetch'
import { randomNumber } from "@/utils/number"
import Breadcrumbs from "@/components/common/breadcrumb"
import commonStyles from "../common.less"
import Desc from "@/components/form/desc"
import DatasetName from "@/components/form/items/datasetName"
import Dataset from '@/components/form/option/Dataset'

function Copy() {
  const [_, getDataset] = useFetch('dataset/getDataset')
  const [createResult, createDataset] = useFetch('dataset/createDataset')
  const [__, clearCache] = useFetch('dataset/clearCache')
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const history = useHistory()
  const location = useLocation()
  const { did } = location.query
  const [form] = Form.useForm()
  const dataset = useSelector(({ dataset }) => dataset.dataset[did])

  useEffect(() => {
    did && getDataset({ id: did })
  }, [did])

  useEffect(() => {
    if (createResult) {
      message.success(t('dataset.copy.success.msg'))
      clearCache()
      const group = createResult.dataset_group_id || ''
      history.replace(`/home/project/${pid}/dataset#${group}`)
    }
  }, [createResult])

  const onFinish = async (values) => {
    const params = {
      ...values,
      pid,
      did,
    }
    createDataset(params)
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
          <Form.Item label={t('dataset.copy.form.dataset')}>
            <Dataset dataset={dataset} />
          </Form.Item>
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

export default Copy
