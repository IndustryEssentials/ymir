interface Config{
  [key: string]: any,
}
const theme = {
  '@primary-color': 'rgb(54, 203, 203)',
  '@btn-primary-bg': 'rgb(44, 189, 233)',
  '@body-background': '#F0F2F5',
  '@link-color': 'rgba(59, 160, 255, 1)',
  '@layout-header-background': "linear-gradient(to right, @primary-color, @btn-primary-bg)",
  '@layout-header-height': '60px',
  '@layout-header-padding': '0 32px',
  '@layout-footer-padding': '15px 100px',
  '@success-color': '@primary-color',
  '@warning-color': 'rgb(250, 211, 55)',
  '@error-color': 'rgb(242, 99, 123)',
  "@radio-button-active-color": '@primary-color',
  '@card-shadow': '0 1px 2px -2px fade(@primary-color, 16), 0 3px 6px 0 fade(@primary-color, 12), 0 5px 12px 4px fade(@primary-color, 9)',
}

export default theme
