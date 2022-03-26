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

const { useForm } = Form

const InitModel = (props) => {
  const history = useHistory()
  const pageParams = useParams()
  const id = Number(pageParams.id)

  const [form] = useForm()

  async function submit(values) {

    const params = {
      ...values,
      id,
    }
    console.log('params:', params)
    const result = await props.updateProject(params)
    if (result) {
      message.success(t('dataset.add.success.msg'))
      history.push(`/home/project/detail/${id}`)
    }
  }

  return (
    <div className={s.wrapper}>
      <Breadcrumbs />
      <Card className={s.container} title={t('project.iteration.initmodel')}>
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
            <ConfigProvider renderEmpty={() => <EmptyStateModel id={id} />}>
              <Tip content={t('tip.task.filter.model')}>
                <Form.Item
                  label={t('task.mining.form.model.label')}
                  name="model"
                  rules={[
                    { required: true, message: t('task.mining.form.model.required') },
                  ]}
                >
                  <ModelSelect placeholder={t('task.mining.form.mining.model.required')} pid={id} />
                </Form.Item>
              </Tip>
            </ConfigProvider>
            <Tip hidden={true}>
              <Form.Item wrapperCol={{ offset: 8 }}>
                <Space size={20}>
                  <Form.Item name='submitBtn' noStyle>
                    <Button type="primary" size="large" htmlType="submit">
                      {t('common.confirm')}
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
    updateProject: (payload) => {
      return dispatch({
        type: 'project/updateProject',
        payload,
      })
    },
  }
}

export default connect(null, actions)(InitModel)
