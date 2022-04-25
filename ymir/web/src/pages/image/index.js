import React, { useEffect, useState } from "react"
import styles from "./index.less"
import { useHistory, useLocation, useParams } from "umi"
import { Form, Input, Radio, Card, } from "antd"

import t from "@/utils/t"
import { getImageTypes } from '@/constants/query'
import Breadcrumbs from "@/components/common/breadcrumb"
import ImageList from './components/list'
import { SearchIcon } from "@/components/common/icons"
import ShareImageList from "./components/shareImageList"

const { useForm } = Form

const tabsTitle = [
  { tab: t('image.tab.my.title'), key: 'my', },
  { tab: t('image.tab.public.title'), key: 'public', },
]

const initQuery = {
  name: undefined,
  type: undefined,
  offset: 0,
  limit: 20,
}

function Image() {
  const { keyword } = useParams()
  const history = useHistory()
  const location = useLocation()
  const [form] = useForm()
  const [active, setActive] = useState(tabsTitle[0].key)
  const [query, setQuery] = useState(initQuery)

  const types = getImageTypes().map(type => ({ ...type, label: t(type.label) }))

  useEffect(() => {
    if (keyword) {
      setQuery(old => ({ ...old, name: keyword }))
      form.setFieldsValue({ name: keyword })
    }
  }, [keyword])

  useEffect(() => {
    const type = location?.state?.type
    if (typeof type !== 'undefined') {
      setActive(type)
    }
  }, [location.state])


  const search = (values) => {
    const name = values.name
    if (typeof name === 'undefined') {
      setQuery((old) => ({
        ...old,
        ...values,
        offset: initQuery.offset,
      }))
    } else {
      setTimeout(() => {
        if (name === form.getFieldValue('name')) {
          setQuery((old) => ({
            ...old,
            name,
            offset: initQuery.offset,
          }))
        }
      }, 1000)
    }
  }

  const resetQuery = () => {
    setQuery(initQuery)
    form.resetFields()
  }

  const contents = {
    my: <ImageList filter={query} />,
    public: <ShareImageList />,
  }

  const searchPanel = (
    <Form
      name='queryForm'
      form={form}
      layout="inline"
      initialValues={{ name: keyword || "" }}
      onValuesChange={search}
      colon={false}
    >
      <Form.Item
        name="type"
        label={t("image.column.type")}
      >
        <Radio.Group options={types} optionType="button"></Radio.Group>
      </Form.Item>
      <Form.Item name="name" label={t('image.query.name')}>
        <Input placeholder={t("image.query.name.placeholder")} allowClear suffix={<SearchIcon />} />
      </Form.Item>
    </Form>
  )

  return (
    <div className={styles.image}>
      <Breadcrumbs />
      <Card tabList={tabsTitle} activeTabKey={active} onTabChange={(key) => { history.replace({ state: { type: key } }); resetQuery() }} tabBarExtraContent={active === 'my' ? searchPanel : null}>
        {contents[active]}
      </Card>
    </div>
  )
}

export default Image
