import React from "react"
import { Button, Col, Row, Space } from "antd"
import { Link, useSelector } from "umi"

import t from "@/utils/t"
import { getStepLabel } from "@/constants/iteration"
import useFetch from "@/hooks/useFetch"

import s from "../detail.less"
import { EditIcon, SearchEyeIcon, EyeOffIcon } from "@/components/common/Icons"
import { ArrowDownIcon, ArrowRightIcon } from "@/components/common/Icons"

function ProjectDetail({ project = {} }) {
  const id = project.id

  const unfold = useSelector(({ iteration }) => iteration.actionPanelExpand)
  const [_, toggleActionPanel] = useFetch("iteration/toggleActionPanel", true)

  return (
    <div className={s.detailContainer}>
      <Row>
        <Col flex={1}>
          <Space className={s.detailPanel} wrap size={16}>
            <span className={s.name}>{project.name}</span>
            <span className={s.iterationInfo}>
              {t("project.detail.info.iteration", {
                stageLabel: (
                  <span className={s.orange}>
                    {t(getStepLabel(project.currentStep?.name, project.round))}
                  </span>
                ),
                current: <span className={s.orange}>{project.round}</span>,
              })}
            </span>
            <span>
              {t("project.train_classes")}:{" "}
              <span className={s.black}>{project?.keywords?.join(",")}</span>
            </span>
            {project.description ? (
              <span>
                {t("project.detail.desc")}: {project.description}
              </span>
            ) : null}
          </Space>
        </Col>
        <Col>
          <Link to={`/home/project/${id}/iterations/settings`}>
            <EditIcon />
            <span>{t("project.iteration.settings.title")}</span>
          </Link>
          <Button type="link" onClick={() => toggleActionPanel(!unfold)}>
            {unfold ? (
              <>
                <ArrowDownIcon />
                {t(`iteration.fold`)}
              </>
            ) : (
              <>
                <ArrowRightIcon />
                {t(`iteration.unfold`)}
              </>
            )}
          </Button>
        </Col>
      </Row>
    </div>
  )
}
export default ProjectDetail
