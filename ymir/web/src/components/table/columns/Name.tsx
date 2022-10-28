import { Popover } from "antd"
import { Link } from "umi"
import { ColumnType } from "antd/lib/table"

import t from '@/utils/t'
import { DescPop } from "@/components/common/DescPop"
import StrongTitle from "./StrongTitle"
import { Dataset } from "@/interface/dataset"

const Name = (type = 'dataset'): ColumnType<Dataset> => ({
  title: StrongTitle(`${type}.column.name`),
  dataIndex: "versionName",
  render: (name, { id, name: groupName, projectId: pid, description }) => {
    const popContent = <DescPop description={description} style={{ maxWidth: '30vw' }} />
    const content = <Link to={`/home/project/${pid}/${type}/${id}`}>{groupName} {name}</Link>
    return description ? <Popover title={t('common.desc')} content={popContent}>
      {content}
    </Popover> : content
  },
  ellipsis: true,
})

export default Name
