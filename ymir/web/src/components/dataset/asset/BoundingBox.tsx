import { Col, Popover, Row, Space } from 'antd'
import { FC, useEffect, useRef, useState } from 'react'

import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'

import styles from '../common.less'

type Props = {
  annotation: YModels.BoundingBox
  ratio?: number
}

const BoundingBox: FC<Props> = ({ annotation, ratio = 1 }) => {
  const popContent = (annotation: YModels.BoundingBox) => {
    const evaluatedLabel = evaluationLabel(annotation.cm)
    const tags = annotation.tags || {}
    const tagsArr = Object.keys(tags)
    return (
      <>
        <Row>
          <Col flex={'100px'}>{t('keyword.column.name')}</Col>
          <Col flex={1}>{annotation.keyword}</Col>
        </Row>
        {evaluatedLabel ? (
          <Row>
            <Col flex={'100px'}>Evaluation</Col>
            <Col flex={1}>{evaluationLabel(annotation.cm)}</Col>
          </Row>
        ) : null}
        {annotation.score ? (
          <Row>
            <Col flex={'100px'}>{t('model.verify.confidence')}</Col>
            <Col flex={1}>{annotation.score}</Col>
          </Row>
        ) : null}
        {tagsArr.length ? (
          <Row>
            <Col flex={'100px'}>{t('dataset.assets.keyword.selector.types.tags')}</Col>
            <Col flex={1}>
              {tagsArr.map((tag) => (
                <Space key={tag} style={{ width: '100%' }}>
                  <span style={{ fontWeight: 'bold' }}>{tag}: </span> <span>{tags[tag]}</span>
                </Space>
              ))}
            </Col>
          </Row>
        ) : null}
      </>
    )
  }
  const { x, y, w, h } = annotation.box
  return (
    <Popover content={popContent} placement="right">
      <div
        title={`${annotation.keyword}` + (annotation.score ? `\nConference:${annotation.score}` : '')}
        className={`${styles.annotation} ${annotation.gt ? styles.gt : ''}`}
        style={{
          color: annotation.color,
          borderColor: annotation.color,
          boxShadow: `${annotation.color} 0 0 2px 1px`,
          top: y * ratio,
          left: x * ratio,
          width: w * ratio - 2,
          height: h * ratio - 2,
        }}
      >
        <span className={styles.annotationTitle} style={{ backgroundColor: annotation.color }}>
          {annotation.keyword}
          {annotation.score ? <> {annotation.score}</> : null}
        </span>
      </div>
    </Popover>
  )
}

export default BoundingBox
