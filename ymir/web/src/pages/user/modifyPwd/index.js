import React, { useEffect, useState } from "react"
import { connect } from "dva"
import { Form, Input, Button } from "antd"
import styles from "../common.less"
import { formLayout } from "@/config/antd"
import t from "@/utils/t"

const pwdRepeat = ({ getFieldValue }) => ({
  validator(_, value) {
    if (value && getFieldValue("password") !== value) {
      return Promise.reject(t("signup.pwd.repeat.same.msg"))
    }
    return Promise.resolve()
  },
})

const ModifyPwd = ({ token, title = "Modify Password", modifyPwd, history }) => {
  const onFinish = async ({ repwd, password }) => {
    var params = {
      token,
      repwd,
      password,
    }
    const res = await modifyPwd(params)
    if (res) {
      history.push("/home/portal")
    }
  }

  const onFinishFailed = (errorInfo) => {
    console.log("Failed:", errorInfo)
  }

  return (
    <div className={styles.loginWrap}>
      <div className={styles.container}>
        <div className={styles.wrapper}>
          <Form
            {...formLayout}
            name="basic"
            initialValues={{}}
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
          >
            <Form.Item wrapperCol={{ offset: 6 }}>
              <h3>{title}</h3>
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
                  min: 6,
                  max: 20,
                  message: t("signup.pwd.length.msg"),
                },
              ]}
            >
              <Input.Password />
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
              <Input.Password />
            </Form.Item>

            <Form.Item wrapperCol={{ offset: 6 }}>
              <Button type="primary" htmlType="submit" block>
                {title}
              </Button>
            </Form.Item>
          </Form>
        </div>
      </div>
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
export default connect(null, mapDispatchToProps)(ModifyPwd)
