import { Space } from "antd"
import t from "@/utils/t"
import s from "../detail.less"
import { TestingSet } from "./testingSet"

const NoIterationDetail = ({ project }) => {
  return (
    <div className={s.header}>
      <Space className={s.detailPanel} wrap size={16}>
        <span className={s.name}>{project.name}</span>
        <span className={s.type}>{t('project.types.label')}: {t(project.typeLabel)}</span>
        <span>{t('project.train_classes')}: <span className={s.black}>{project?.keywords?.join(',')}</span></span>
        {project.description ? <span>{t('project.detail.desc')}: {project.description}</span> : null}
      </Space>
      <TestingSet project={project} />
    </div>
  )
}

export default NoIterationDetail
