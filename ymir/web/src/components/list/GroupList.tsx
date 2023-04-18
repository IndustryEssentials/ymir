import { FC, useEffect, useState } from 'react'
import { Col, Pagination, Row } from 'antd'
import styles from './groupList.less'
import { ArrowDownIcon, ArrowRightIcon } from '@/components/common/Icons'
import GroupActions from './GroupActions'
import DatasetItems from './DatasetItems'
import { useSelector } from 'umi'
import useRequest from '@/hooks/useRequest'
import { List } from '@/models/typings/common'

type Group = YModels.Group & {
  projectLabel?: string
}
type Props = {
  module: 'dataset' | 'model'
  pid: number
  list: List<YModels.Group>
  initVisible?: boolean
  project?: YModels.Project
}

const GroupList: FC<Props> = ({ module = 'dataset', pid, initVisible, children }) => {
  const isDataset = module === 'dataset'
  const [visible, setVisible] = useState(initVisible)
  const [groups, setGroups] = useState<Group[]>([])
  const [total, setTotal] = useState(1)
  const { [pid]: list } = useSelector(({ dataset, model }) => (isDataset ? dataset.datasets : model.models))
  const project = useSelector(({ project }) => project.projects[pid])
  const query = useSelector((state) => state[module].query)
  const { run: updateQuery } = useRequest(`${module}/updateQuery`)

  useEffect(() => {
    let groups = list.items
    if (list) {
    }
    if (project) {
      // add extra project info
    }
    setGroups(groups)
  }, [project, list])

  useEffect(() => {
    setTotal(list.total)
  }, [list])

  const freshGroup = (group: Group) => {
    const index = groups.findIndex(({ id }) => id === group.id)
    setGroups(groups.splice(index, 1, group))
  }

  const pagerChange = (current: number, pageSize: number) => {
    const limit = pageSize
    const offset = (current - 1) * pageSize
    updateQuery({ ...query, limit, offset, current })
  }

  return (
    <>
      <div className="groupList">
        {groups.map((group) => (
          <div className={styles.groupItem} key={group.id}>
            <Row className="groupTitle">
              <Col flex={1} onClick={() => setVisible((v) => !v)}>
                <span className="foldBtn">{visible ? <ArrowDownIcon /> : <ArrowRightIcon />} </span>
                <span className="groupName">{group.name}</span>
                {group.projectLabel ? <span className={styles.extraTag}>{group.projectLabel}</span> : null}
              </Col>
              <Col>
                <GroupActions group={group} fresh={(newGroup) => freshGroup(newGroup)} />
              </Col>
            </Row>
            <div className="groupTable" hidden={!visible}>
              <DatasetItems gid={group.id} />
            </div>
          </div>
        ))}
      </div>
      <Pagination
        className={`pager ${styles.pager}`}
        showQuickJumper
        showSizeChanger
        total={total}
        current={query.current}
        pageSize={query.limit}
        onChange={pagerChange}
      />
    </>
  )
}

export default GroupList
