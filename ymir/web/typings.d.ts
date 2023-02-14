declare module '*.css'
declare module '*.less'
declare module '*.png'
declare module '@/assets/icons/iconfont'
declare module '*.svg' {
  export function ReactComponent(
    props: React.SVGProps<SVGSVGElement>,
  ): React.ReactElement;
  const url: string;
  export default url;
}

  interface Window {
    baseConfig: {
      [name: string]: string
    }
  }
