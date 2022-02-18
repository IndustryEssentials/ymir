import React, {  } from "react"
import styles from "./index.less"
import { useHistory } from "umi"
import { Form } from "antd"

import Breadcrumbs from "@/components/common/breadcrumb"
import List from './components/list'

const { useForm } = Form

function Project() {
  const history = useHistory()

  return (
    <div className={styles.project}>
      <Breadcrumbs />
      <List />
    </div>
  )
}

export default Project
