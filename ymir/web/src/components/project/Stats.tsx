import { Col, Row } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import { Project } from '@/constants'

type StatType = {
  label: string
  count?: number
}

const numStyles = {
  height: 44,
  fontSize: 28,
  color: 'rgba(0, 0, 0, 0.85)',
}

const Stats: FC<{ type: 'dataset' | 'model'; project: Project }> = ({ type, project }) => {
  const statBlocks = (blocks: StatType[] = []) =>
    blocks.map((block, index) =>
      typeof block.count !== 'undefined' ? (
        <Col key={index} span={24 / blocks.length}>
          {statBlock(block)}
        </Col>
      ) : null,
    )

  const statBlock = ({ label, count }: StatType) => (
    <>
      <div className="contentLabel">{t(label)}</div>
      <div className="contentCount" style={numStyles}>
        {count}
      </div>
    </>
  )

  return (
    <Row className="content" justify="center" style={{ textAlign: 'center' }}>
      {statBlocks([
        { label: `project.stats.${type}s.total`, count: project[`${type}Count`] },
        { label: `project.stats.${type}s.processing`, count: project[`${type}ProcessingCount`] },
        { label: `project.stats.${type}s.invalid`, count: project[`${type}ErrorCount`] },
        { label: `project.stats.${type}s.assets.total`, count: type === 'dataset' ? project.totalAssetCount : undefined },
      ])}
    </Row>
  )
}

export default Stats
