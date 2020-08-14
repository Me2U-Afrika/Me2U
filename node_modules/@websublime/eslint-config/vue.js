const baseRules = require('./rules/base');
const vueRules = require('./rules/vue');

const parser = 'vue-eslint-parser';

const configs = [
  'plugin:vue/essential',
  'plugin:vue/recommended',
  'plugin:vue/strongly-recommended',
	'plugin:@typescript-eslint/recommended',
	'plugin:import/typescript',
	// Disable rules which might conflict with Prettier
	'prettier',
  'prettier/@typescript-eslint'
];

const plugins = [
  'jest',
  'new-with-error',
  'sort-class-members',
  'simple-import-sort',
  'sort-destructure-keys',
  'sort-imports-es6',
  'switch-case',
  '@typescript-eslint'
];

module.exports = {
  'env': {
    'browser': true,
    'es6': true,
    'node': true
  },
  parser,
  "parserOptions": {
    "parser": "babel-eslint",
    "ecmaVersion": 2017,
    "sourceType": "module"
  },
	extends: configs,
	plugins,
	rules: {
		...baseRules,
		...vueRules,
	},
};
