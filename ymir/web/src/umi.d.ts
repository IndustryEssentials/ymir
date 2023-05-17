import umi from 'umi'
import Stores from '@/models/'
declare module 'umi' {
  type SelectorType = <R extends (state: Stores) => any>(selector: R) => ReturnType<R>
  const useSelector: SelectorType
}
