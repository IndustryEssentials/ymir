import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Card, Input, Button, Form, Row, Col, List, Modal, message } from "antd"

import t from "@/utils/t"
import Breadcrumbs from "@/components/common/breadcrumb"
import Uploader from '@/components/form/uploader'
import { phoneValidate } from "@/components/form/validators"
import s from "./common.less"
import { EmailIcon, KeyIcon, LockIcon, SmartphoneIcon, UserIcon } from "@/components/common/icons"

const { useForm } = Form

function Info({ user, updateUserInfo, validatePwd, modifyPwd, getToken, }) {

  const [infoList, setInfoList] = useState([])
  const [usernameModify, setUsernameModify] = useState(false)
  const [phoneModify, setPhoneModify] = useState(false)
  const [passwordModify, setPasswordModify] = useState(false)
  const [usernameForm] = useForm()
  const [phoneForm] = useForm()
  const [passwordForm] = useForm()


  useEffect(() => {
    transUserIntoList()
  }, [user])

  function transUserIntoList() {
    setInfoList([
      {
        key: 'username', title: t('user.info.list.username'), value: user.username, icon: <UserIcon />,
        action: () => { setUsernameModify(true) }
      },
      { key: 'email', title: t('user.info.list.email'), value: user.email, icon: <EmailIcon />, color: 'rgb(233, 192, 28)' },
      {
        key: 'phone', title: t('user.info.list.phone'), value: user.phone, icon: <SmartphoneIcon />,
        color: 'rgb(44, 189, 233)', action: () => { setPhoneModify(true) }
      },
      {
        key: 'password', title: t('user.info.list.password'), value: '********', icon: <LockIcon />,
        action: () => { setPasswordModify(true) }
      },
      // { key: 'permission', title: t('user.info.list.permission'), value: 'role', icon: <UserSettingsIcon />, action: () => { } },
    ])
  }

  const onUsernameOk = () => {
    // submit
    usernameForm.validateFields().then(async () => {
      const username = usernameForm.getFieldValue('username').trim()
      const result = await updateUserInfo({ username })
      if (result) {
        setUsernameModify(false)
        message.success(t('user.info.username.success'))
      }
    })
  }
  const onAvatarOk = async (files, url) => {
    // submit
    if (url) {
      const result = await updateUserInfo({ avatar: url })
      if (result) {
        message.success(t('user.info.avatar.success'))
      } else {
        message.error(t('user.info.avatar.failure'))
      }
    } else {
      message.error(t('user.info.avatar.empty'))
    }
  }
  const onPhoneOk = () => {
    phoneForm.validateFields().then(async () => {
      const phone = phoneForm.getFieldValue('phone')
      const result = await updateUserInfo({ phone })
      if (result) {
        setPhoneModify(false)
        message.success(t('user.info.phone.success'))
      }
    })
  }
  const onPasswordOk = () => {
    passwordForm.validateFields().then(async () => {
      const { old_password, password } = passwordForm.getFieldsValue()
      const oldRes = await validatePwd(user.email, old_password)
      if (oldRes?.access_token) {
        const result = await modifyPwd(password)
        if (result) {
          await getToken(user.email, password)
          setPasswordModify(false)
          message.success(t('user.info.pwd.success'))
        } else {
          message.error(t('user.info.pwd.failed'))
        }
      } else {
        message.error(t('user.info.pwd.error'))
      }
    })
  }

  const onUsernameCancel = () => setUsernameModify(false)
  const onPhoneCancel = () => setPhoneModify(false)
  const onPasswordCancel = () => setPasswordModify(false)

  const pwdRepeat = ({ getFieldValue }) => ({
    validator(_, value) {
      if (value && getFieldValue("password") !== value) {
        return Promise.reject(t("signup.pwd.repeat.same.msg"))
      }
      return Promise.resolve()
    },
  })

  const setIcon = (icon, color = '') => <div className={s.icon} style={{ background: color }}>{icon}</div>

  const renderItem = ({ title, key, icon, color, value, action }) => {
    return (
      <List.Item key={key}>
        <List.Item.Meta
          avatar={setIcon(icon, color)}
          title={title}
          description={value}
        />
        {key !== 'email' ? <Button type='link' onClick={action}>{t('common.modify')}</Button> : null}
      </List.Item>
    )
  }

  return (
    <div className={s.info}>
      <Breadcrumbs />
      <Card className={s.container} title={t('breadcrumbs.user.info')}>
        <Row className={s.content}>
          <Col flex={1} md={{ span: 20, justify: 'center' }} lg={{ offset: 6, span: 12 }} xl={{ offset: 4, span: 12, }}>
            <Row className={s.avatarContent} justify='center'>
              <Col flex={1}>
                <div className={s.avatar}>{user.avatar ? <img src={user.avatar} /> : <UserIcon style={{ color: '#fff', fontSize: 70 }} />}</div>
                <Uploader
                  onChange={onAvatarOk}
                  format='avatar'
                  crop={true}
                  max={20}
                  info={t('user.info.avatar.tip')}
                  showUploadList={false}
                ></Uploader>
              </Col>
            </Row>
            <List className={s.infoList} dataSource={infoList} renderItem={renderItem}></List>
          </Col>
        </Row>
      </Card>
      <Modal destroyOnClose title={t('user.info.list.username')} visible={usernameModify} onCancel={onUsernameCancel} onOk={onUsernameOk}>
        <Form
          form={usernameForm}
          name='usernameForm'
          labelAlign='left'
          size='large'
          preserve={false}
        >
          <Form.Item
            name="username"
            initialValue={user.username}
            rules={[
              { required: true, whitespace: true, message: t("signup.username.required.msg"), },
              { min: 2, max: 15, message: t("signup.username.length.msg", { max: 15 }), },
            ]}
          >
            <Input allowClear placeholder={t('signup.username.placeholder')} prefix={<UserIcon />} />
          </Form.Item>
        </Form>
      </Modal>
      <Modal title={t('user.info.list.phone')} visible={phoneModify} onCancel={onPhoneCancel} onOk={onPhoneOk} destroyOnClose>
        <Form
          form={phoneForm}
          name='phoneForm'
          labelAlign='left'
          size='large'
          preserve={false}
        >
          <Form.Item
            name="phone"
            initialValue={user.phone}
            rules={[{ validator: phoneValidate }]}
          >
            <Input allowClear placeholder={t('signup.phone.placeholder')} prefix={<SmartphoneIcon />} />
          </Form.Item>
        </Form>
      </Modal>
      <Modal title={t('user.info.list.password')} visible={passwordModify} onCancel={onPasswordCancel} onOk={onPasswordOk} destroyOnClose>

        <Form
          form={passwordForm}
          name='passwordForm'
          labelAlign='left'
          size='large'
          preserve={false}
        >
          <Form.Item
            name="old_password"
            rules={[
              { required: true, message: t("signup.pwd.required.msg"), },
              { min: 8, max: 16, message: t("signup.pwd.length.msg", { min: 8, max: 16 }), },
            ]}
          >
            <Input.Password visibilityToggle={false} allowClear placeholder={t('user.info.pwd.form.old')} prefix={<KeyIcon />} />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[
              { required: true, message: t("signup.pwd.required.msg"), },
              { type: 'string', min: 8, max: 16, message: t("signup.pwd.length.msg", { min: 8, max: 16 }), },
            ]}
          >
            <Input.Password visibilityToggle={false} allowClear placeholder={t('user.info.pwd.form.new')} prefix={<LockIcon />} />
          </Form.Item>
          <Form.Item
            name="repwd"
            dependencies={["password"]}
            rules={[
              { required: true, message: t("signup.pwd.repeat.required.msg"), },
              pwdRepeat,
            ]}
          >
            <Input.Password visibilityToggle={false} allowClear placeholder={t('user.info.pwd.form.renew')} prefix={<LockIcon />} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

const props = (state) => {
  return {
    user: state.user,
  }
}

const acts = (dispatch) => {
  return {
    updateUserInfo(info) {
      return dispatch({
        type: 'user/updateUserInfo',
        payload: info,
      })
    },
    modifyPwd(password) {
      return dispatch({
        type: 'user/modifyPwd',
        payload: password,
      })
    },
    getToken(username, password) {
      return dispatch({
        type: 'user/getToken',
        payload: { username, password, }
      })
    },
    validatePwd(username, password) {
      return dispatch({
        type: 'user/getToken',
        payload: { username, password }
      })
    }
  }
}

export default connect(props, acts)(Info)
