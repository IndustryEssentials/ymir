import React from "react"
import { Row, Col, } from "antd"

import ProjectChart from "./projectChart"
import MyProjects from './projectMy'
import PublicSets from './datasetOrigin'
import ModelList from "./modelList"

import styles from "./index.less"

function Portal({ }) {

  return (
    <div className={styles.portal}>
      <Row className={styles.dataset_panel} gutter={20}>
        <Col span={16}>
          <MyProjects />
        </Col>
        <Col span={8}>
          <div className={styles.dataset_panel}>
            <PublicSets />
          </div>
          <div className={styles.model_panel}>
            <ModelList />
          </div>
          <div>
            <ProjectChart></ProjectChart>
          </div>
        </Col>
      </Row>
    </div>
  )
}

export default Portal
