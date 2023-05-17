import { Col, Row } from 'antd'
import { FC } from 'react'
import t from '@/utils/t'
import Chart, { Props as ChartConfigType } from './Chart'
import style from './analysis.less'
export type ChartType = ChartConfigType & { label: string }
type Props = {
  label: string
  charts: ChartType[]
}

const ChartsContainer: FC<Props> = ({ label, charts }) =>
  charts?.length ? (
    <>
      <h3>{t(label)}</h3>
      <Row gutter={[10, 20]}>
        {charts.map((chart) => (
          <Col span={24} key={chart.label}>
            <div className={style.echartTitle}>{t(chart.label)}</div>
            <Chart customOptions={chart.customOptions} height={300} />
          </Col>
        ))}
      </Row>
    </>
  ) : null

export default ChartsContainer
