import React, { useEffect, useState } from 'react'
import { Select, Input, Form, Row, Col, Checkbox } from 'antd'
import { useHistory, useParams, Link, useSelector } from 'umi'

import { formLayout } from '@/config/antd'
import { getLabelToolUrl } from '@/constants/common'
import t from '@/utils/t'
import Uploader from '@/components/form/uploader'
import useRequest from '@/hooks/useRequest'

import DatasetSelect from '@/components/form/datasetSelect'
import Desc from '@/components/form/desc'
import Tip from '@/components/form/tip'
import SubmitButtons from './SubmitButtons'
import MergeType from '@/components/form/items/MergeType'
import KeepAnnotations from './label/KeepAnnotations'
import UserKeywordsSelector from '@/components/form/UserKeywordsSelector'

import styles from './label.less'

const { Item } = Form

function Label({ query = {}, hidden, ok = () => {}, bottom }) {
  const pageParams = useParams()
  const pid = Number(pageParams.id)
  const { iterationId, type, url } = query
  const did = Number(query.did)
  const [doc, setDoc] = useState(undefined)
  const [form] = Form.useForm()
  const [asChecker, setAsChecker] = useState(false)
  const { data: project, run: getProject } = useRequest('project/getProject', { loading: false })
  const { data: created, run: label } = useRequest('task/label')

  useEffect(() => {
    created && ok(created)
  }, [created])

  useEffect(() => {
    const desc = url ? [{ name: url.replace(/^.*\/([^\/]+)$/, '$1') }] : undefined
    form.setFieldsValue({
      datasetId: did || undefined,
      keepAnnotations: type ? type : 0,
      desc,
    })
    url && setDoc(url)
  }, [did])

  useEffect(() => {
    // iteration context
    iterationId && pid && getProject({ id: pid })
  }, [pid])

  useEffect(() => {
    project && form.setFieldsValue({ keywords: project.keywords })
  }, [project])

  const onFinish = (values) => {
    const { labellers, checker } = values
    const emails = [labellers]
    checker && emails.push(checker)
    const params = {
      ...values,
      projectId: pid,
      labellers: emails,
      doc,
    }
    const result = label(params)
    result && ok(result)
  }

  function docChange(files, docFile) {
    setDoc(files.length ? location.protocol + '//' + location.host + docFile : '')
  }

  function onFinishFailed(errorInfo) {
    console.log('Failed:', errorInfo)
  }

  const initialValues = {
    datasetId: did || undefined,
    keepAnnotations: type,
  }
  return (
    <div>
      <Form
        className={styles.form}
        {...formLayout}
        form={form}
        name="labelForm"
        initialValues={initialValues}
        onFinish={onFinish}
        onFinishFailed={onFinishFailed}
      >
        <div hidden={hidden}>
          <Item wrapperCol={{ span: 20 }}>
            <Tip content={t('task.label.header.tip')} />
          </Item>
          <MergeType form={form} disabledNew={!!iterationId} />
          <Item label={t('task.fusion.form.dataset')} name="datasetId">
            <DatasetSelect pid={pid} />
          </Item>
          {false ? (
            <Item label={t('task.label.form.member')} tooltip={t('tip.task.filter.labelmember')} required>
              <Row gutter={20}>
                <Col flex={1}>
                  <Item
                    name="labellers"
                    noStyle
                    rules={[
                      {
                        required: true,
                        message: t('task.label.form.member.required'),
                      },
                      {
                        type: 'email',
                        message: t('task.label.form.member.email.msg'),
                      },
                    ]}
                  >
                    <Input placeholder={t('task.label.form.member.placeholder')} allowClear />
                  </Item>
                </Col>
                <Col style={{ lineHeight: '30px' }}>
                  <Checkbox checked={asChecker} onChange={({ target }) => setAsChecker(target.checked)}>
                    {t('task.label.form.plat.checker')}
                  </Checkbox>
                </Col>
              </Row>
            </Item>
          ) : null}
          <Item hidden={!asChecker} tooltip={t('tip.task.filter.labelplatacc')} label={t('task.label.form.plat.label')} required>
            <Row gutter={20}>
              <Col flex={1}>
                <Item
                  name="checker"
                  noStyle
                  rules={
                    asChecker
                      ? [
                          {
                            required: true,
                            message: t('task.label.form.member.required'),
                          },
                          {
                            type: 'email',
                            message: t('task.label.form.member.email.msg'),
                          },
                        ]
                      : []
                  }
                >
                  <Input placeholder={t('task.label.form.member.labelplatacc')} allowClear />
                </Item>
              </Col>
              <Col>
                <a target="_blank" href={getLabelToolUrl()}>
                  {t('task.label.form.plat.go')}
                </a>
              </Col>
            </Row>
          </Item>
          <Item
            label={t('task.label.form.target.label')}
            tooltip={t('tip.task.filter.labeltarget')}
            name="keywords"
            rules={[
              {
                required: true,
                message: t('task.label.form.target.placeholder'),
              },
            ]}
          >
            <UserKeywordsSelector />
          </Item>
          <KeepAnnotations />
          <Item label={t('task.label.form.desc.label')} name="desc">
            <Uploader
              onChange={docChange}
              onRemove={() => setDoc(undefined)}
              format="doc"
              max={50}
              info={t('task.label.form.desc.info', { br: <br /> })}
            ></Uploader>
          </Item>
          <Desc form={form} />
        </div>
        <Item wrapperCol={{ offset: 8 }}>
          {bottom ? bottom : <SubmitButtons label="common.action.label" />}
          <div className={styles.bottomTip}>
            {t('task.label.bottomtip', {
              link: (
                <Link target="_blank" to={getLabelToolUrl()}>
                  {t('task.label.bottomtip.link.label')}
                </Link>
              ),
            })}
          </div>
        </Item>
      </Form>
    </div>
  )
}

export default Label
