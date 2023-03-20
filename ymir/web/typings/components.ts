declare namespace YComponents {
  // components table actions
  type Action = {
    key: string,
    label?: string,
    onclick?: Function,
    icon?: React.ReactElement,
    link?: string,
    target?: string,
    disabled?: boolean,
    hidden?: Function,
  }

  type ComponentsTableActionsProps = {
    actions: Action[],
    showCount?: number,
  }

}