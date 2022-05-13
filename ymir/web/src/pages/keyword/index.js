import React, { useEffect, useRef, useState } from "react"
import { connect } from 'dva'
import styles from "./index.less"
import { Link, useHistory, useParams } from "umi"
import { Form, Button, Input, Select, Table, Menu, Dropdown, Space, Modal, ConfigProvider, Row, Col, Radio, Tooltip, } from "antd"
import {
  PlusOutlined,
  SearchOutlined,
  SyncOutlined,
} from "@ant-design/icons"

import t from "@/utils/t"
import { format } from '@/utils/date'
import Breadcrumbs from "@/components/common/breadcrumb"
import EmptyState from '@/components/empty/keyword'
import Actions from "@/components/table/actions"
import Add from './add'
import MultiAdd from "./multiAdd"
import { AddIcon, AddtaskIcon, EditIcon, SearchIcon, } from "@/components/common/icons"


const { confirm } = Modal
const { useForm } = Form

const initQuery = {
  name: "",
  offset: 0,
  limit: 20,
}

function Keyword({ getKeywords }) {
  const history = useHistory()
  const [keywords, setKeywords] = useState([])
  const [total, setTotal] = useState(0)
  const [form] = useForm()
  const [query, setQuery] = useState(initQuery)
  const [showAdd, setShowAdd] = useState(false)
  const [selected, setSelected] = useState([])
  const multiAddRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    getData()
  }, [query])

  useEffect(() => {
    const state = history.location.state
    if (state?.type === 'add') {
      setShowAdd(true)
      history.replace({ state: {}})
    }
  }, [ history.location.state ])

  const columns = [
    {
      title: showTitle("keyword.column.name"),
      dataIndex: "name",
      ellipsis: true,
    },
    {
      title: showTitle("keyword.column.alias"),
      dataIndex: "aliases",
      render: (keywords) => {
        const label = t('dataset.column.keyword.label', { keywords: keywords.join(', '), total: keywords.length })
        return <Tooltip key={label} placement='left' title={label}
          color='white' overlayInnerStyle={{ color: 'rgba(0,0,0,0.45)', fontSize: 12 }}
          mouseEnterDelay={0.5}
        >{label}</Tooltip>
      },
      ellipsis: {
        showTitle: false,
      },
    },
    {
      title: showTitle('keyword.column.update_time'),
      dataIndex: 'update_time',
      render: (time) => time ? format(time) : null,
    },
    {
      title: showTitle('keyword.column.create_time'),
      dataIndex: 'create_time',
      render: (time) => time ? format(time) : null,
    },
    {
      title: showTitle("keyword.column.action"),
      dataIndex: "action",
      render: (text, record) => <Actions menus={actionMenus(record)} />,
      className: styles.tab_actions,
      align: "center",
      width: "280px",
    },
  ]

  const pageChange = ({ current, pageSize }) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    setQuery((old) => ({ ...old, limit, offset }))
  }

  function showTitle(str) {
    return <strong>{t(str)}</strong>
  }

  async function getData() {
    let params = {
      offset: query.offset,
      limit: query.limit,
    }
    if (query.name) {
      params.q = query.name.toLowerCase()
    }
    const { items, total } = await getKeywords(params)
    if (items) {
      setKeywords(() => items)
      setTotal(total)
    }
  }

  const actionMenus = (record) => {
    return [
      {
        key: "edit",
        label: t("dataset.action.edit"),
        onclick: () => edit(record),
        icon: <EditIcon />,
      },
    ]
  }

  const edit = (record) => {
    setSelected([record])
    setShowAdd(true)
  }

  const add = () => {
    setShowAdd(true)
  }

  const multiAdd = () => {
    multiAddRef.current.show()
  }

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

  const addBtn = (
    <Button type="primary" onClick={add}>
      <AddIcon /> {t("keyword.add.label")}
    </Button>
  )
  const multiAddBtn = (
    <Button type="primary" onClick={multiAdd}>
      <AddIcon /> {t("keyword.multiadd.label")}
    </Button>
  )

  return (
    <div className={styles.keyword}>
      <Breadcrumbs />

      <Space className='actions'>
        {addBtn}
        {multiAddBtn}
      </Space>
      <div className={`list ${styles.list}`}>
        <div className={`search ${styles.search}`}>
          <Form
            name='queryForm'
            form={form}
            // layout="inline"
            labelCol={{ flex: '120px' }}
            onValuesChange={search}
            colon={false}
          >
            <Row>
              <Col className={styles.queryColumn} span={12}>
                <Form.Item name="name" label={t("keyword.column.name")}>
                  <Input placeholder={t("keyword.query.name.placeholder")} style={{ width: '80%' }} allowClear suffix={<SearchIcon />} />
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </div>

        <Row className={styles.refresh}>
          <Col flex={1}>
          </Col>
          <Col>
            <Button
              type='text'
              icon={<SyncOutlined style={{ color: 'rgba(0, 0, 0, 0.45)' }} />}
              title={'Refresh'}
              onClick={() => getData()}
            ></Button>
          </Col>
        </Row>
        <div className={styles.table}>
          <ConfigProvider renderEmpty={() => <EmptyState />}>
            <Table
              dataSource={keywords}
              onChange={({ current, pageSize }) =>
                pageChange({ current, pageSize })
              }
              rowKey={(record) => record.name}
              rowClassName={(record, index) => index % 2 === 0 ? '' : 'oddRow'}
              pagination={{
                showQuickJumper: true,
                showSizeChanger: true,
                total: total,
                // total: 500,
                defaultPageSize: query.limit,
                showTotal: (total) => t("keyword.pager.total.label", { total }),
                defaultCurrent: 1,
              }}
              columns={columns}
            ></Table>
          </ConfigProvider>
        </div>
        <Add visible={showAdd} keys={selected} cancel={() => { setShowAdd(false); setSelected([]) }} ok={() => { resetQuery(); getData() }} />
        <MultiAdd ref={multiAddRef} ok={() => getData()} />

      </div>
    </div>
  )
}

const props = (state) => {
  return {
    logined: state.user.logined,
  }
}

const actions = (dispatch) => {
  return {
    getKeywords: (payload) => {
      return dispatch({
        type: 'keyword/getKeywords',
        payload,
      })
    },
  }
}

export default connect(props, actions)(Keyword)
