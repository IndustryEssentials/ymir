import umi from 'umi'
declare module 'umi' {
  type SelectorType = <R extends (state: YStates.Root) => any>(selector: R) => ReturnType<R>
  const useSelector: SelectorType
}