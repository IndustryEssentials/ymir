declare module '*.css'
declare module '*.less'
declare module '*.png'
declare module 'react-xml-viewer'
declare module '@/assets/icons/iconfont' {
  const iconUrl: string
  export default iconUrl
}
declare module '*.svg' {
  export function ReactComponent(props: React.SVGProps<SVGSVGElement>): React.ReactElement
  const url: string
  export default url
}

declare module '*.json' {
  const data: any
  export default data
}

interface Window {
  baseConfig: {
    [name: string]: string
  }
}
