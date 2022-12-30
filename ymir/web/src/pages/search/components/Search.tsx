import Name from '@/components/search/Name'
import { Col, Form, Row } from 'antd'
import { FC } from 'react'
import State from '@/components/search/State'
import ObjectType from '@/components/search/ObjectType'
import Time from '@/components/search/Time'


type Props = {
  change?: (query: YParams.ResultListQuery) => void
}

const { Item } = Form

const Search: FC<Props> = ({ change }) => {
  const [form] = Form.useForm<YParams.ResultListQuery>()
  const valuesChange = (_: any, values: any) => {
    const query: YParams.ResultListQuery = valueHandle(values)
    console.log('search comp. query:', query)
    change && change(query)
  }

  const valueHandle = (values: any = {}): YParams.ResultListQuery => {
    const getTimestamp = (date?: moment.Moment) => date && date.format('X')
    const [start, end] = values.time || []
    return {
      ...values,
      startTime: getTimestamp(start),
      endTime: getTimestamp(end),
    }
  }
  return (
    <Form form={form} onValuesChange={valuesChange} className='box' style={{ marginBottom: 0 }}>
      <Row gutter={10}>
        <Col flex={1}>
          <Item name={'name'} noStyle>
            <Name />
          </Item>
        </Col>
        <Col>
          <Item name={'state'} noStyle>
            <State />
          </Item>
        </Col>

        <Col>
          <Item name={'objectType'} noStyle>
            <ObjectType />
          </Item>
        </Col>
        <Col>
          <Item name={'time'} noStyle>
            <Time />
          </Item>
        </Col>
      </Row>
    </Form>
  )
}

export default Search
