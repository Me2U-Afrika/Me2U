const baseRules = require('./rules/base');
const reactRules = require('./rules/react');

const configs = [
	'airbnb',
	// Disable rules which might conflict with Prettier
	'prettier',
	'prettier/react',
];

const plugins = [
  'jest',
  'new-with-error',
  'react-hooks',
  'react',
  'sort-class-members',
  'sort-destructure-keys',
  'sort-imports-es6',
  'switch-case'
];

module.exports = {
  extends: configs,
  env: {
    es6: true,
    jasmine: true,
    jest: true,
    node: true
  },
	plugins,
	rules: {
		...baseRules,
		...reactRules,
	},
};
