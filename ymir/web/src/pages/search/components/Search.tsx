import Name from '@/components/search/Name'
import { Button, Col, Form, Row } from 'antd'
import { FC, useEffect, useState } from 'react'
import State from '@/components/search/State'
import Time from '@/components/search/Time'
import { useDebounce } from 'ahooks'

import t from '@/utils/t'

type Props = {
  change?: (query?: YParams.ResultListQuery) => void
  name?: string
}

type DateType = moment.Moment | undefined

const { Item } = Form

const Search: FC<Props> = ({ change, name }) => {
  const [form] = Form.useForm<YParams.ResultListQuery>()
  const [searchName, setSearchName] = useState<string>()
  const debonceName = useDebounce(searchName, { wait: 500 })
  const [query, setQuery] = useState<YParams.ResultListQuery>({})
  const valuesChange = (changed: any, values: any) => {
    if (typeof changed.name !== 'undefined') {
      setSearchName(changed.name)
      delete changed.name
      delete values.name
    }
    if (changed && Object.keys(changed).length) {
      const query: YParams.ResultListQuery = valueHandle(values)
      setQuery(query)
      updateQuery(query)
    }
  }

  const valueHandle = (values: any = {}): YParams.ResultListQuery => {
    const getTimestamp = (date: DateType) => date && date.format('X')
    const [start, end]: [DateType, DateType] = values.time || []
    return {
      ...values,
      startTime: getTimestamp(start?.startOf('day')),
      endTime: getTimestamp(end?.endOf('day')),
      offset: 0
    }
  }

  useEffect(() => {
    typeof debonceName !== 'undefined' && updateQuery({ ...query, name: debonceName, offset: 0 })
  }, [debonceName])

  useEffect(() => {
    name && form.setFieldsValue({ name })
    name && setSearchName(name)
  }, [name])

  function updateQuery(q?: YParams.ResultListQuery) {
    change && change(q)
  }

  function reset() {
    form.resetFields()
    setQuery({})
    updateQuery()
  }

  return (
    <Form form={form} onValuesChange={valuesChange} className="box" style={{ marginBottom: 0 }}>
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
          <Item name={'time'} noStyle>
            <Time />
          </Item>
        </Col>
        <Col>
          <Item name={'time'} noStyle>
            <Button onClick={reset}>{t('common.reset')}</Button>
          </Item>
        </Col>
      </Row>
    </Form>
  )
}

export default Search
