declare module '*.css';
declare module '*.less';
declare module '*.png';
declare module '*.svg' {
  export function ReactComponent(
    props: React.SVGProps<SVGSVGElement>,
  ): React.ReactElement;
  const url: string;
  export default url;
}
// components table actions
type Action = {
  key: string, 
  label: string, 
  onclick?: Function,
  icon?: string, 
  link?: string, 
  target?: string,
  disabled?: boolean,
  hidden?: Function,
}

type ComponentsTableActionsProps = {
  actions: Action[],
  showCount?: number,
}
