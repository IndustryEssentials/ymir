import { Col, Row, Space } from "antd"
import { Link } from "umi"
import t from "@/utils/t"
import s from "../detail.less"
import { EditIcon, EyeOffIcon } from "@/components/common/Icons"
import { TestingSet } from "./testingSet"

const NoIterationDetail = ({ project }) => {
  return (
    <div className={s.detailContainer}>
      <Space className={s.detailPanel} wrap size={16}>
        <span className={s.name}>{project.name}</span>
        <span>{t('project.train_classes')}: <span className={s.black}>{project?.keywords?.join(',')}</span></span>
        {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
      </Space>
      <TestingSet project={project} />
    </div>
  )
}

export default NoIterationDetail
