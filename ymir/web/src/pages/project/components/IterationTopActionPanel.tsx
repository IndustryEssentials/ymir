import { FC } from 'react'
import { Link, useParams } from 'umi'
import {useSelector } from 'react-redux'
import { Button } from 'antd'
import t from '@/utils/t'
import { EditIcon, SearchEyeIcon, EyeOffIcon } from '@/components/common/Icons'
import { ArrowDownIcon, ArrowRightIcon } from '@/components/common/Icons'
import useRequest from '@/hooks/useRequest'
import TrainingClassesSelector from './TrainingCalssesSelector'

const IterationTopActionPanel: FC<{ fold?: boolean}> = ({ fold }) => {
  const { id } = useParams<{ id: string }>()
  const unfold = useSelector<YStates.Root, boolean>(({ iteration }) => iteration.actionPanelExpand)
  const { run: toggleActionPanel } = useRequest<boolean, [boolean]>('iteration/toggleActionPanel')
  return (
    <>
    <TrainingClassesSelector pid={Number(id)} />
      <Link to={`/home/project/${id}/iterations/settings`}>
        <EditIcon />
        <span>{t('project.iteration.settings.title')}</span>
      </Link>
      {fold ? <Button type="link" onClick={() => toggleActionPanel(!unfold)}>
        {unfold ? <ArrowDownIcon /> : <ArrowRightIcon />}
        {t(`iteration.${unfold ? 'unfold' : 'fold'}`)}
      </Button> : null }
    </>
  )
}

export default IterationTopActionPanel
