import React from "react"
import { Row, Col, } from "antd"

import TaskChart from "./taskChart"
import TaskList from './taskList'
import MySets from './datasetMy'
import PublicSets from './datasetOrigin'
import ModelHot from "./modelHot"
import ModelList from "./modelList"

import styles from "./index.less"

function Portal({ }) {

  return (
    <div className={styles.portal}>
      <Row className={styles.dataset_panel} gutter={20}>
        <Col span={16}>
          <MySets />
        </Col>
        <Col span={8}>
          <PublicSets />
        </Col>
      </Row>
      <Row className={styles.model_panel} gutter={20}>
        <Col span={16}>
          <ModelHot></ModelHot>
        </Col>
        <Col span={8}>
          <ModelList />
        </Col>
      </Row>
      <Row className={styles.task_panel} gutter={20}>
        <Col span={16}>
          <TaskList />
        </Col>
        <Col span={8}>
          <TaskChart></TaskChart>
        </Col>
      </Row>
    </div>
  )
}

export default Portal
