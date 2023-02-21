import { FC, ReactNode, useEffect, useRef, useState } from 'react'
import { Row, Space } from 'antd'

import DefaultEmpty from '@/components/empty/default'

import styles from '../assets.less'
import Item from './AssetListItem'
import VisualModes from './VisualModes'

type Props = {
  list?: YModels.Asset[]
  goAsset?: (asset: YModels.Asset, hash: string, current: number) => void
  mode?: VisualModes
  width?: number
  columns?: number
  pager?: ReactNode
}

const ItemSpace = 4

const List: FC<Props> = ({ list = [], goAsset = () => {}, mode, columns = 5, pager }) => {
  const [rows, setRows] = useState<YModels.Asset[][]>([])
  const [width, setWidth] = useState(0)
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let r = 0
    let result: YModels.Asset[][] = []
    while (r < list.length) {
      result.push(list.slice(r, r + columns))
      r += columns
    }
    setRows(result)
  }, [list, columns])

  useEffect(() => {
    listRef.current?.clientWidth && setWidth(listRef.current.clientWidth)
  }, [listRef.current?.clientWidth])

  window.addEventListener('resize', () => listRef.current && setWidth(listRef.current.clientWidth))

  return (
    <div className={styles.listContainer} ref={listRef}>
      {rows.length ? (
        <>
          <div>
            {rows.map((row, index) => {
              const h =
                (width - ItemSpace * columns) /
                row.reduce((prev, asset) => {
                  const { width = 0, height = 0 } = asset?.metadata || {}
                  return height ? prev + width / height : prev
                }, 0)

              return (
                <Row gutter={ItemSpace} wrap={false} key={columns * (index + 1)} className={styles.dataset_container}>
                  {row.map((asset, rowIndex) => (
                    <Item
                      asset={asset}
                      key={index * columns + rowIndex}
                      showDetail={() => goAsset(asset, asset.hash, index * columns + rowIndex)}
                      height={h}
                      mode={mode}
                    />
                  ))}
                </Row>
              )
            })}
          </div>
          <Space className={styles.pagi}>{pager}</Space>
        </>
      ) : (
        <DefaultEmpty />
      )}
    </div>
  )
}

export default List
