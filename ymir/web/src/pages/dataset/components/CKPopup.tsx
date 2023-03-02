import type { FC } from "react"
import CustomLabels from "@/components/dataset/asset/CustomLabels"
import { Popover } from "antd"
import t from '@/utils/t'

type Props = {
  asset?: YModels.Asset
}

const CkPopup: FC<Props> = ({ asset, children }) => {
  const cks = Object.keys(asset?.cks || {})
  const content = (
    <>
      <h4>{t('dataset.assets.keyword.selector.types.cks')}</h4>
      <CustomLabels asset={asset} />
    </>
  )
  return cks.length ? (
    <Popover placement="bottomLeft" content={content}>
      {children}
    </Popover>
  ) : (
    <>{children}</>
  )
}

export default CkPopup
