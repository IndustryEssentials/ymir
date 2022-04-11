import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Form, Input, Button, Layout, Row, Col } from "antd"
import { useParams, useHistory } from "umi"

import t from "@/utils/t"
import { layout420 } from "@/config/antd"
import HeaderNav from "@/components/nav"
import Foot from "@/components/common/footer"
import styles from "../common.less"

const { Header, Footer, Content } = Layout

const ResetPwd = ({ resetPwd }) => {
  const history = useHistory()
  const { token } = useParams()
  const onFinish = async ({ password }) => {
    var params = {
      token,
      new_password: password,
    }
    const res = await resetPwd(params)
    if (res) {
      history.push("/login")
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo)
  }

  const repeatErr = t("signup.pwd.repeat.same.msg")

  const pwdRepeat = ({ getFieldValue }) => ({
    validator(_, value) {
      if (value && getFieldValue("password") !== value) {
        return Promise.reject(repeatErr)
      }
      return Promise.resolve()
    },
  })
  return (
    <div className={styles.reset}>
      <Layout>
        <Header>
          <HeaderNav simple></HeaderNav>
        </Header>
        <Content className={styles.content}>
          <div className={styles.formBox}>
            <Row className={styles.header}>
              <Col flex={1}>
                <h2>{t("reset_pwd.title.page")}</h2>
              </Col>
              <Col>
                <Button type="link" onClick={() => history.replace('/login')}>
                  {t("reset_pwd.back")}
                </Button>
              </Col>
            </Row>
            <Form
              className={styles.form}
              {...layout420}
              name="resetForm"
              initialValues={{}}
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
              size="large"
              labelAlign='left'
            >
              <Form.Item>
                <h3>{t("reset_pwd.tip.title")}</h3>
                <p>{t('reset_pwd.tip.content')}</p>
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
                    min: 8,
                    max: 16,
                    message: t("signup.pwd.length.msg", { min: 8, max: 16 }),
                  },
                ]}
              >
                <Input.Password visibilityToggle={false} allowClear placeholder={t('reset_pwd.pwd.placeholder')} />
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
                <Input.Password visibilityToggle={false} allowClear placeholder={t('reset_pwd.repwd.placeholder')} />
              </Form.Item>

              <Form.Item name='submitBtn' wrapperCol={{ span: 24 }}>
                <Button type="primary" htmlType="submit" className={styles.submit} block>
                  {t("reset_pwd.reset")}
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
    resetPwd(params) {
      return dispatch({
        type: "user/resetPwd",
        payload: params,
      })
    },
  }
}
export default connect(null, mapDispatchToProps)(ResetPwd)
