import React, {  } from "react"
import styles from "./index.less"
import { useHistory } from "umi"

import Breadcrumbs from "@/components/common/breadcrumb"
import List from './components/list'

function Project() {
  return (
    <div className={styles.project}>
      <Breadcrumbs />
      <List />
    </div>
  )
}

export default Project
