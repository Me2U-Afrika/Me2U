const baseRules = require('./rules/base');

const configs = [
	'airbnb-base',
	// Disable rules which might conflict with Prettier
	'prettier',
];

const plugins = [
  'jest',
  'new-with-error',
  'react-hooks',
  'react',
  'simple-import-sort',
  'sort-class-members',
  'sort-destructure-keys',
  'sort-imports-es6',
  'switch-case'
];

module.exports = {
  env: {
    es6: true,
    jasmine: true,
    jest: true,
    node: true
  },
	extends: configs,
	plugins,
	rules: baseRules,
};
