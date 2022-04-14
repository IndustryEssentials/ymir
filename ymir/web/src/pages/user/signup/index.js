import React from "react"
import { connect } from "dva"
import { useIntl, Link } from "umi"
import { Form, Input, Button, Checkbox, Layout, Row, Col, message } from "antd"

import t from "@/utils/t"
import { STATES } from '@/constants/user'
import { layout420 } from "@/config/antd"
import HeaderNav from "@/components/nav"
import Foot from "@/components/common/footer"
import styles from "../common.less"
import { EmailIcon, UserIcon, SmartphoneIcon, LockIcon, KeyIcon } from '@/components/common/icons'
import { phoneValidate } from "@/components/form/validators"

const { Header, Footer, Content } = Layout

const Signup = ({ signupApi, loginApi, history }) => {

  const pwdRepeat = ({ getFieldValue }) => ({
    validator(_, value) {
      if (value && getFieldValue("password") !== value) {
        return Promise.reject(t("signup.pwd.repeat.same.msg"))
      }
      return Promise.resolve()
    },
  })
  const signup = async ({ email, username, phone = '', password }) => {
    const params = {
      email,
      username: username.trim(),
      phone: phone.trim(),
      password,
    }
    const res = await signupApi(params)
    if (res) {
      history.push("/login")
      if (res.state === STATES.ACTIVE) {
        message.success(t('user.signup.success.active'))
      } else {
        message.warn(t('user.signup.success'))
      }
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo)
  }

  return (
    <div className={styles.reg}>
      <Layout>
        <Header>
          <HeaderNav simple></HeaderNav>
        </Header>
        <Content className={styles.content}>
          <div className={styles.formBox}>
            <Row className={styles.header}>
              <Col flex={1}>
                <h2>{t("signup.title.page")}</h2>
              </Col>
              <Col className={styles.back}>
                {t('signup.login.tip')}<Link to={"/login"}>{t('signup.login.label')}</Link>
              </Col>
            </Row>
            <Form
              className={styles.form}
              {...layout420}
              name="signupForm"
              initialValues={{}}
              onFinish={signup}
              onFinishFailed={onFinishFailed}
              labelAlign='left'
              size='large'
            >
              <Form.Item
                label={t("signup.email")}
                name="email"
                rules={[
                  {
                    required: true,
                    message: t("signup.email.required.msg"),
                  },
                  {
                    type: "email",
                    message: t("signup.email.format.msg"),
                  },
                ]}
              >
                <Input allowClear placeholder={t('signup.email.placeholder')} prefix={<EmailIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
              </Form.Item>
              <Form.Item
                label={t("signup.username")}
                name="username"
                rules={[
                  {
                    required: true,
                    whitespace: true,
                    message: t("signup.username.required.msg"),
                  },
                  {
                    min: 2,
                    max: 15,
                    message: t("signup.username.length.msg", { max: 15 }),
                  },
                ]}
              >
                <Input allowClear placeholder={t('signup.username.placeholder')} prefix={<UserIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
              </Form.Item>
              <Form.Item
                label={t("signup.phone")}
                name="phone"
                rules={[{ validator: phoneValidate }]}
              >
                <Input allowClear placeholder={t('signup.phone.placeholder')} prefix={<SmartphoneIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
              </Form.Item>

              <Form.Item
                label={t("signup.pwd")}
                name="password"
                rules={[
                  {
                    required: true,
                    message: t("signup.pwd.required.msg"),
                  },
                  {
                    type: 'string',
                    min: 8,
                    max: 16,
                    message: t("signup.pwd.length.msg", {min: 8, max: 16}),
                  },
                ]}
              >
                <Input.Password allowClear visibilityToggle={false} placeholder={t('signup.pwd.placeholder')} prefix={<LockIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
              </Form.Item>
              <Form.Item
                label={t("signup.repwd")}
                name="repwd"
                dependencies={["password"]}
                rules={[
                  {
                    required: true,
                    message: t("signup.pwd.repeat.required.msg"),
                  },
                  pwdRepeat,
                ]}
              >
                <Input.Password allowClear visibilityToggle={false} placeholder={t('signup.repwd.placeholder')} prefix={<KeyIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
              </Form.Item>

              <Form.Item name='submitBtn' wrapperCol={{ span: 24 }}>
                <Button type="primary" htmlType="submit" className={styles.submit} block>
                  {t("signup.signup")}
                </Button>
              </Form.Item>
            </Form>
          </div>
        </Content>
        <Footer>
          <Foot></Foot>
        </Footer>
      </Layout>
    </div>
  )
}

const mapDispatchToProps = (dispatch) => {
  return {
    signupApi(params) {
      return dispatch({
        type: "user/signup",
        payload: params,
      })
    },
    loginApi(params) {
      return dispatch({
        type: "user/login",
        payload: params,
      })
    },
  }
}
export default connect(null, mapDispatchToProps)(Signup)
