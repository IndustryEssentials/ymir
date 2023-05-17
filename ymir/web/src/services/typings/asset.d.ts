import { evaluationTags } from '@/constants/asset'
import { DatasetsQuery } from './common'

interface AssetQueryParams extends DatasetsQuery {
  id: number | string
  cm?: evaluationTags[]
  exclude?: number[]
  annoType?: number
  type?: string
}
