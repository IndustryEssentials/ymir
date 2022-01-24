import React from "react"
import { connect } from "dva"
import { Form, Input, Button, Layout, Row, Col } from "antd"
import { useHistory } from "umi"

import t from "@/utils/t"
import { layout420 } from "@/config/antd"
import HeaderNav from "@/components/nav"
import Foot from "@/components/common/footer"
import styles from "../common.less"
import { EmailIcon } from "@/components/common/icons"

const { Header, Footer, Content } = Layout

const Forget = ({ forgetPwd }) => {
  const history = useHistory()
  const onFinish = async ({ email }) => {
    const res = await forgetPwd(email)
    if (res) {
      history.replace("/login")
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo)
  }

  return (
    <div className={styles.forget}>
      <Layout>
        <Header>
          <HeaderNav simple></HeaderNav>
        </Header>
        <Content className={styles.content}>
          <div className={styles.formBox}>
            <Row className={styles.header}>
              <Col flex={1}>
                <h2>{t("forget.title.page")}</h2>
              </Col>
              <Col>
                <Button type="link" onClick={() => history.goBack()}>
                  {t("common.back")}&gt;
                </Button>
              </Col>
            </Row>
            <Form
              className={styles.form}
              {...layout420}
              name="forgetForm"
              initialValues={{}}
              onFinish={onFinish}
              onFinishFailed={onFinishFailed}
              size="large"
              labelAlign='left'
            >
              <Form.Item>
                <h3 className={styles.tipTitle}>{t("forget.title")}</h3>
                <p className={styles.tip}>{t("forget.info")}</p>
              </Form.Item>
              <Form.Item
                label={t("forget.email")}
                name="email"
                rules={[
                  {
                    required: true,
                    message: t("forget.email.required.msg"),
                  },
                  { email: true, message: t("forget.email.valid.msg") },
                ]}
              >
                <Input allowClear prefix={<EmailIcon style={{ color: 'rgba(0, 0, 0, 0.45)'}} />} placeholder={t('forget.email.placeholder')}  />
              </Form.Item>
              <Form.Item name='submitBtn' wrapperCol={{ span: 24 }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  className={styles.submit}
                  block
                >
                  {t("forget.send")}
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
    forgetPwd(email) {
      return dispatch({
        type: "user/forgetPwd",
        payload: email,
      })
    },
  }
}
export default connect(null, mapDispatchToProps)(Forget)
