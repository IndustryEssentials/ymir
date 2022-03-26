import { Button, Card, Form, message, Select, Space, ConfigProvider } from 'antd'
import { connect } from 'dva'
import { useParams, useHistory } from 'umi'

import { formLayout } from "@/config/antd"
import t from '@/utils/t'
import EmptyStateModel from '@/components/empty/model'
import ModelSelect from "@/components/form/modelSelect"
import s from './add.less'
import Breadcrumbs from '@/components/common/breadcrumb'
import Tip from "@/components/form/tip"

const { Option } = Select
const { useForm } = Form

const TYPES = Object.freeze({
  INTERNAL: 1,
  SHARE: 2,
  NET: 3,
  LOCAL: 4,
  PATH: 5,
})


const InitModel = (props) => {
  const history = useHistory()
  const pageParams = useParams()
  const pid = Number(pageParams.pid)

  const [form] = useForm()

  async function submit(values) {

    const result = await props.createDataset(params)
    if (result) {
      message.success(t('dataset.add.success.msg'))
      props.clearCache()
      history.push(`/home/project/detail/${pid}`)
    }
  }

  function onFinishFailed(err) {
    console.log('finish failed: ', err)
  }


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
            onFinish={submit}
            labelAlign={'left'}
            colon={false}
          >
            <ConfigProvider renderEmpty={() => <EmptyStateModel />}>
              <Tip content={t('tip.task.filter.model')}>
                <Form.Item
                  label={t('task.mining.form.model.label')}
                  name="model"
                  rules={[
                    { required: true, message: t('task.mining.form.model.required') },
                  ]}
                >
                  <ModelSelect placeholder={t('task.mining.form.mining.model.required')} pid={pid} />
                </Form.Item>
              </Tip>
            </ConfigProvider>
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
              </Form.Item>
            </Tip>
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
    clearCache() {
      return dispatch({ type: "dataset/clearCache", })
    },
    updateKeywords: (payload) => {
      return dispatch({
        type: 'keyword/updateKeywords',
        payload,
      })
    },
  }
}

export default connect(null, actions)(InitModel)
