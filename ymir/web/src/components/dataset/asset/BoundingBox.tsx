import { Col, Popover, Row, Space } from 'antd'
import { FC, ReactNode, useEffect, useRef, useState } from 'react'

import t from '@/utils/t'
import { evaluationLabel } from '@/constants/dataset'

import styles from '../common.less'
import { percent } from '@/utils/number'

type Props = {
  annotation: YModels.BoundingBox
  ratio?: number
  simple?: boolean
}

const BoundingBox: FC<Props> = ({ annotation, ratio = 1, simple = false }) => {
  const popContent = () => {
    const evaluatedLabel = evaluationLabel(annotation?.cm)
    const tags = annotation?.tags || {}
    const tagsArr = Object.keys(tags)
    return (
      <>
        <Row>
          <Col flex={'100px'}>{t('keyword.column.name')}</Col>
          <Col flex={1}>{annotation?.keyword}</Col>
        </Row>
        {evaluatedLabel ? (
          <Row>
            <Col flex={'100px'}>Evaluation</Col>
            <Col flex={1}>{evaluationLabel(annotation?.cm)}</Col>
          </Row>
        ) : null}
        {annotation?.score ? (
          <Row>
            <Col flex={'100px'}>{t('model.verify.confidence')}</Col>
            <Col flex={1} title={`${annotation.score}`}>{percent(annotation?.score)}</Col>
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
  const width = w * ratio <= 2 ? 1 : w * ratio - 2
  const height = h * ratio <= 2 ? 1 : h * ratio - 2

  const getBox = (annotation: YModels.BoundingBox, title = '', extra?: ReactNode) => (
    <div
      title={title}
      className={`${styles.annotation} ${annotation.gt ? styles.gt : ''}`}
      style={{
        color: annotation.color,
        borderColor: annotation.color,
        boxShadow: `${annotation.color} 0 0 2px 1px`,
        top: y * ratio,
        left: x * ratio,
        width,
        height,
      }}
    >
      {extra}
    </div>
  )
  const box = simple
    ? getBox(annotation)
    : getBox(
        annotation,
        `${annotation.keyword}` + (annotation.score ? `\nConference:${annotation.score}` : ''),
        <span className={styles.annotationTitle} style={{ backgroundColor: annotation.color }}>
          {annotation.keyword}
          {annotation.score ? <> {annotation.score}</> : null}
        </span>,
      )
  return simple ? (
    box
  ) : (
    <Popover content={popContent()} placement="right">
      {box}
    </Popover>
  )
}

export default BoundingBox
