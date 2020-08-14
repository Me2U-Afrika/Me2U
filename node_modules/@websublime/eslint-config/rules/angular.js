module.exports = {
  '@typescript-eslint/class-name-casing': 'error',
  '@typescript-eslint/consistent-type-definitions': 'error',
  '@typescript-eslint/explicit-member-accessibility': [
    'off',
    {
      accessibility: 'explicit'
    }
  ],
  '@typescript-eslint/member-ordering': 'error',
  '@typescript-eslint/no-empty-function': 'off',
  '@typescript-eslint/no-empty-interface': 'error',
  '@typescript-eslint/no-inferrable-types': 'error',
  '@typescript-eslint/no-misused-new': 'error',
  '@typescript-eslint/no-non-null-assertion': 'error',
  '@typescript-eslint/prefer-function-type': 'error',
  '@typescript-eslint/unified-signatures': 'error',
  'arrow-body-style': ['error', 'as-needed'],
  camelcase: 'off',
  'constructor-super': 'error',
  'dot-notation': 'off',
  eqeqeq: ['error', 'smart'],
  'guard-for-in': 'error',
  'id-blacklist': 'off',
  'id-match': 'off',
  'import/no-deprecated': 'warn',
  //'import/order': 'error',
  'no-bitwise': 'error',
  'no-caller': 'error',
  'no-console': [
    'error',
    {
      allow: [
        'log',
        'dirxml',
        'warn',
        'error',
        'dir',
        'timeLog',
        'assert',
        'clear',
        'count',
        'countReset',
        'group',
        'groupCollapsed',
        'groupEnd',
        'table',
        'Console',
        'markTimeline',
        'profile',
        'profileEnd',
        'timeline',
        'timelineEnd',
        'timeStamp',
        'context'
      ]
    }
  ],
  'no-debugger': 'error',
  'no-empty': 'off',
  'no-eval': 'error',
  'no-fallthrough': 'error',
  'no-new-wrappers': 'error',
  'no-shadow': [
    'error',
    {
      hoist: 'all'
    }
  ],
  'no-throw-literal': 'error',
  'no-undef-init': 'error',
  'no-underscore-dangle': 'off',
  'no-unused-expressions': 'error',
  'no-var': 'error',
  'prefer-const': 'error',
  radix: 'error',
  /* '@typescript-eslint/tslint/config': [
    'error',
    {
      rules: {
        'component-class-suffix': true,
        'component-selector': [true, 'element', 'app', 'kebab-case'],
        'directive-class-suffix': true,
        'directive-selector': [true, 'attribute', 'app', 'camelCase'],
        'import-blacklist': [true, 'rxjs/Rx'],
        'no-host-metadata-property': true,
        'no-input-rename': true,
        'no-inputs-metadata-property': true,
        'no-output-on-prefix': true,
        'no-output-rename': true,
        'no-outputs-metadata-property': true,
        'nx-enforce-module-boundaries': [
          true,
          {
            allow: [],
            depConstraints: [
              {
                onlyDependOnLibsWithTags: ['*'],
                sourceTag: '*'
              }
            ]
          }
        ],
        'object-literal-sort-keys': [true, 'match-declaration-order'],
        typedef: [true, 'call-signature'],
        'use-lifecycle-interface': true,
        'use-pipe-transform-interface': true
      }
    }
  ] */
};
