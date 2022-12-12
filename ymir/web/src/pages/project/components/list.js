import React, { useEffect, useRef, useState } from "react"
import { connect } from "dva"
import { useHistory } from "umi"
import {
  List,
  Space,
  Pagination,
  Card,
  Button,
  Form,
  Input,
  message,
  ConfigProvider,
} from "antd"

import t from "@/utils/t"
import ProjectEmpty from "@/components/empty/project"
import Del from "./del"
import Item from "@/components/project/list/Item"
import s from "./list.less"
import {
  EditIcon,
  DeleteIcon,
  AddIcon,
  SearchIcon,
} from "@/components/common/Icons"

const ProjectList = ({ list, query, ...func }) => {
  const history = useHistory()
  const [projects, setProjects] = useState([])
  const [total, setTotal] = useState(1)
  const [form] = Form.useForm()
  const delRef = useRef(null)

  /** use effect must put on the top */
  useEffect(() => {
    setProjects(list.items)
    setTotal(list.total)
  }, [list])

  useEffect(() => {
    if (history.action !== "POP") {
      initState()
    }
  }, [history.location])

  useEffect(() => {
    getData()
  }, [query])

  const pageChange = (current, pageSize) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    func.updateQuery({ ...query, current, limit, offset })
  }

  async function getData() {
    await func.getProjects(query)
  }

  const moreList = (record) => {
    const { id, name } = record

    const menus = [
      {
        key: "edit",
        label: t("project.action.edit"),
        onclick: (e) => {
          e.stopPropagation()
          history.push(`/home/project/${id}/add`)
        },
        icon: <EditIcon />,
      },
      {
        key: "del",
        label: t("project.action.del"),
        onclick: (e) => {
          e.stopPropagation()
          del(id, name)
        },
        icon: <DeleteIcon />,
      },
    ]

    return menus
  }

  const del = (id, name) => {
    delRef.current.del(id, name)
  }

  const search = ({ name = "" }) => {
    setTimeout(() => {
      if (name === form.getFieldValue("name")) {
        func.updateQuery({ ...query, name: name.trim() })
      }
    }, 1000)
  }

  const delOk = (id) => {
    setProjects(projects.filter((project) => project.id !== id))
    setTotal((old) => old - 1)
    getData()
  }

  const addExample = async () => {
    const result = await func.addExampleProject()
    if (result) {
      message.success(t("project.create.success"))
      getData()
    }
  }

  async function initState() {
    await func.resetQuery()
    form.resetFields()
  }

  const more = (item) => {
    return (
      <Space>
        {moreList(item)
          .filter((menu) => !(menu.hidden && menu.hidden()))
          .map((action) => (
            <a
              type="link"
              className={action.className}
              key={action.key}
              onClick={action.onclick}
              title={action.label}
            >
              {action.icon}
            </a>
          ))}
      </Space>
    )
  }

  const addBtn = (
    <Space className="actions">
      <Button
        className={s.addBtn}
        type="primary"
        onClick={() => history.push("/home/project/add")}
        icon={<AddIcon />}
      >
        {t("project.new.label")}
      </Button>
      <Button
        className={s.addBtn}
        type="primary"
        onClick={() => addExample()}
        icon={<AddIcon />}
      >
        {t("project.new.example.label")}
      </Button>
    </Space>
  )

  const searchPanel = (
    <Form
      name="queryForm"
      form={form}
      layout="inline"
      onValuesChange={search}
      colon={false}
    >
      <Form.Item
        name="name"
        label={t("project.query.name")}
        initialValue={query.name}
      >
        <Input
          style={{ width: "230%" }}
          placeholder={t("project.query.name.placeholder")}
          allowClear
          suffix={<SearchIcon />}
        />
      </Form.Item>
    </Form>
  )

  return (
    <div className={s.projectContent}>
      {addBtn}
      <Card className={s.listContainer}>
        {searchPanel}
        <ConfigProvider
          renderEmpty={() => <ProjectEmpty addExample={addExample} />}
        >
          <List
            className="list"
            dataSource={projects}
            renderItem={project => <Item project={project} more={more(project)} />}
          />
        </ConfigProvider>
        <Pagination
          className="pager"
          onChange={pageChange}
          current={query.current}
          pageSize={query.limit}
          total={total}
          showTotal={() => t("project.list.total", { total })}
          showQuickJumper
          showSizeChanger
        />
        <Del ref={delRef} ok={delOk} />
      </Card>
    </div>
  )
}

const props = (state) => {
  return {
    list: state.project.list,
    query: state.project.query,
  }
}

const actions = (dispatch) => {
  return {
    getProjects: (payload) => {
      return dispatch({
        type: "project/getProjects",
        payload,
      })
    },
    addExampleProject() {
      return dispatch({
        type: "project/addExampleProject",
      })
    },
    updateQuery: (query) => {
      return dispatch({
        type: "project/updateQuery",
        payload: query,
      })
    },
    resetQuery: () => {
      return dispatch({
        type: "project/resetQuery",
      })
    },
  }
}

export default connect(props, actions)(ProjectList)
