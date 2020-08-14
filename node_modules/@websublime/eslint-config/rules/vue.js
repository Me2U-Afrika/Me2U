module.exports = {
  'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
  '@typescript-eslint/ban-ts-ignore': 'off',
  'vue/component-tags-order': ['error', {
    'order': ['template', 'script', 'style']
  }]
};
