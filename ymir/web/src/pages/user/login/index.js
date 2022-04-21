import React from "react"
import { connect } from "dva"
import { Form, Input, Button, Checkbox, Row, Col, Space } from "antd"
import { Link, useHistory, useLocation, getLocale } from "umi"

import { formLayout } from "@/config/antd"
import t from "@/utils/t"
import Foot from "@/components/common/footer"
import styles from "../common.less"
import loginBig from "@/assets/logo-big.png"
import { EmailIcon, LockIcon } from "@/components/common/icons"
import LangBtn from "@/components/common/langBtn"

const Login = ({ loginApi }) => {
  const history = useHistory()
  const location = useLocation()
  const { redirect } = location.query
  const onFinish = async ({ username, password }) => {
    var params = {
      username,
      password,
    }
    const res = await loginApi(params)
    if (res) {
      if (redirect) {
        history.push(redirect)
      } else {
        history.push("/home/portal")
      }
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo)
  }

  return (
    <div className={styles.login}>
      <Row>
        <Col span={16} className={`${styles.slogan} slogan_${getLocale()}`}>
          <div className={styles.logo}><img src={loginBig} /></div>
          <div className={styles.footer}>
            <Foot></Foot>
          </div>
        </Col>
        <Col span={8} className={styles.content}>
          <div className={styles.lang}>
            <LangBtn dark />
          </div>
          <div className={styles.loginForm}>
          <h1 className={styles.title}>{t('login.form.title')}</h1>
          <Form
            className={styles.form}
            name="login"
            initialValues={{}}
            layout='vertical'
            labelCol={{style: { fontWeight: 'bold' }}}
            requiredMark={false}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            size='large'
          >
            <Form.Item
              label={t("login.email")}
              name="username"
              rules={[
                {
                  required: true,
                  message: t("login.email.required.msg"),
                },
              ]}
            >
              <Input allowClear placeholder={t('login.email.placeholder')} prefix={<EmailIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
            </Form.Item>

            <Form.Item
              label={t("login.pwd")}
              name="password"
              rules={[
                {
                  required: true,
                  message: t("login.pwd.required.msg"),
                },
                {
                  type: 'string',
                  // min: 8,
                  max: 16,
                },
              ]}
            >
              <Input.Password allowClear visibilityToggle={false} placeholder={t('login.pwd.placeholder')} prefix={<LockIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} />
            </Form.Item>

            <Form.Item name='submit'>
              <Button type="primary" htmlType="submit" className={styles.submit} block>
                {t("login.login")}
              </Button>
            </Form.Item>
            <Form.Item className={styles.links}>
              <Space>
              <Link className={styles.link} to="/signup">
                {t("login.signup")}
              </Link><span className={styles.link}>|</span>
              <Link className={styles.link} to="/forget_pwd">
                {t("login.forget")}
              </Link>
              </Space>
            </Form.Item>
          </Form>
        
          </div>
        </Col>
      </Row>
    </div>
  )
}

const mapDispatchToProps = (dispatch) => {
  return {
    loginApi(params) {
      return dispatch({
        type: "user/login",
        payload: params,
      })
    },
  }
}
export default connect(null, mapDispatchToProps)(Login)
