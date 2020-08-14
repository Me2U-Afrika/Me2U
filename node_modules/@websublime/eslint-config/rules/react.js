/**
 * Eslint React rules
 */

module.exports = {
  'lines-around-comment': ['error', {
    afterBlockComment: true,
    beforeBlockComment: true
  }],
  'no-console': ['error'],
  'react-hooks/exhaustive-deps': 'error',
  'react-hooks/rules-of-hooks': 'error',
  'react/button-has-type': 'error',
  'react/display-name': 'error',
  'react/jsx-boolean-value': 'error',
  'react/jsx-closing-bracket-location': 'error',
  'react/jsx-curly-brace-presence': ['error', {
    children: 'ignore',
    props: 'always'
  }],
  'react/jsx-curly-spacing': 'error',
  'react/jsx-filename-extension': ['error', {
    extensions: ['.jsx', '.tsx']
  }],
  'react/jsx-first-prop-new-line': ['error', 'multiline-multiprop'],
  'react/jsx-indent': ['error', 2],
  'react/jsx-indent-props': ['error', 2],
  'react/jsx-key': 'error',
  'react/jsx-max-props-per-line': 'error',
  'react/jsx-no-duplicate-props': 'error',
  //'react/jsx-no-literals': 'error',
  'react/jsx-no-undef': 'error',
  'react/jsx-one-expression-per-line': 'off',
  'react/jsx-props-no-spreading': 'off',
  'react/jsx-sort-default-props': 'error',
  'react/jsx-sort-props': 'error',
  'react/jsx-tag-spacing': ['error', {
    afterOpening: 'never',
    beforeClosing: 'allow',
    beforeSelfClosing: 'always',
    closingSlash: 'never'
  }],
  'react/jsx-uses-react': 'error',
  'react/jsx-uses-vars': 'error',
  'react/jsx-wrap-multilines': 'error',
  'react/no-danger': 'error',
  'react/no-direct-mutation-state': 'error',
  'react/no-string-refs': 'error',
  'react/no-unknown-property': 'error',
  'react/prefer-es6-class': 'error',
  'react/prefer-stateless-function': 'error',
  'react/prop-types': ['error', {
    ignore: ['form', 'i18n', 'onSubmit']
  }],
  'react/react-in-jsx-scope': 'error',
  'react/self-closing-comp': 'error',
  'react/sort-comp': ['error', {
    groups: {
      initialization: ['displayName', 'propTypes', 'contextTypes', 'childContextTypes', 'mixins', 'statics', 'defaultProps', 'constructor', 'getDefaultProps', 'state', 'getInitialState', 'getChildContext'],
      lifecycle: ['componentWillMount', 'UNSAFE_componentWillMount', 'componentDidMount', 'componentWillReceiveProps', 'UNSAFE_componentWillReceiveProps', 'shouldComponentUpdate', 'componentWillUpdate', 'UNSAFE_componentWillUpdate', 'getSnapshotBeforeUpdate', 'componentDidUpdate', 'componentDidCatch', 'componentWillUnmount']
    },
    order: ['static-methods', 'initialization', 'everything-else', '/^handle.+$/', 'lifecycle', '/^render.+$/', 'render']
  }],
  'react/sort-prop-types': 'error',
  'react/state-in-constructor': 'off',
  'react/static-property-placement': ['error', 'static public field']
}
