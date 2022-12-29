import Name from '@/components/search/Name'
import { ResultStates } from '@/constants/common'
import { PROJECTTYPES } from '@/constants/project'
import { Col, Form, Row } from 'antd'
import { FC } from 'react'
import State from '@/components/search/State'
import ObjectType from '@/components/search/ObjectType'
import Time from '@/components/search/Time'

type QueryType = {
  name?: string
  objectType?: PROJECTTYPES
  state?: ResultStates
  startTime?: string
  endTime?: string
}
type Props = {
  change?: (query: QueryType) => void
}

const { Item } = Form

const Search: FC<Props> = ({ change }) => {
  const [form] = Form.useForm<QueryType>()
  const valuesChange = (_: any, values: any) => {
    const query: QueryType = valueHandle(values)
    change && change(query)
  }

  const valueHandle = (values: any = {}): QueryType => {
    console.log('values:', values)
    return {
      ...values,
    }
  }
  return (
    <Form form={form} onValuesChange={valuesChange}>
      <Row gutter={10}>
        <Col flex={1}>
          <Item name={'name'}>
            <Name />
          </Item>
        </Col>
        <Col>
          <Item name={'state'}>
            <State />
          </Item>
        </Col>

        <Col>
          <Item name={'objectType'}>
            <ObjectType />
          </Item>
        </Col>
        <Col>
          <Item name={'time'}>
            <Time />
          </Item>
        </Col>
      </Row>
    </Form>
  )
}

export default Search
