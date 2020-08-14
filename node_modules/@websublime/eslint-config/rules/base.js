/**
 * Eslint Base Rules
 */

module.exports = {
  'arrow-body-style': ['error', 'as-needed', {
    requireReturnForObjectLiteral: false
  }],
  'class-methods-use-this': 'off',
  'comma-dangle': ['error', 'only-multiline'],
  curly: ['error', 'all'],
  'id-length': ['error', {
    exceptions: ['_', 'e', 'i', 't']
  }],
  'id-match': ['error', '^_$|^[a-zA-Z][a-zA-Z0-9]*$|^[A-Z][_A-Z0-9]+[A-Z0-9]$', {
    onlyDeclarations: true,
    properties: true
  }],
  'import/order': [
    'error',
    {
      groups: [
        'builtin',
        'external',
        'internal',
        'parent',
        'sibling',
        'index',
      ],
      'newlines-between': 'always',
      alphabetize: { order: 'asc', caseInsensitive: true },
      pathGroups: [
        {
          pattern: 'react',
          group: 'external',
          position: 'before',
        },
        {
          pattern: "@angular/**",
          group: "external",
          position: 'before'
        },
        {
          pattern: "vue",
          group: "external",
          position: 'before'
        }
      ],
      pathGroupsExcludedImportTypes: ['react', 'angular', 'vue']
    }
  ],//'off',
  'import/prefer-default-export': 'off',
  indent: ['error', 2, {
    SwitchCase: 1
  }],
  'import/extensions': [
    'error', 'never', { 'svg': 'always', 'css': 'always', 'scss': 'always' }
  ],
  'jsx-quotes': ['error', 'prefer-single'],
  'lines-around-comment': ['error', {
    afterBlockComment: true,
    beforeBlockComment: true
  }],
  'max-len': ['error', {
    code: 100000,
    comments: 100,
    ignoreComments: false,
    ignoreRegExpLiterals: true,
    ignoreStrings: true,
    ignoreTemplateLiterals: true,
    ignoreTrailingComments: false,
    ignoreUrls: true,
    tabWidth: 2
  }],
  'max-params': ['error', 4],
  'no-console': ['error', {
    allow: ['error']
  }],
  'no-restricted-syntax': ['error', {
    message: 'for..in loops iterate over the entire prototype chain, which is virtually never what you want. Use Object.{keys,values,entries}, and iterate over the resulting array.',
    selector: 'ForInStatement'
  }, {
    message: 'Labels are a form of GOTO; using them makes code confusing and hard to maintain and understand.',
    selector: 'LabeledStatement'
  }, {
    message: '`with` is disallowed in strict mode because it makes code impossible to predict and optimize.',
    selector: 'WithStatement'
  }],
  'object-curly-newline': 'off',
  'prefer-arrow-callback': ['error', {
    allowNamedFunctions: false,
    allowUnboundThis: true
  }],
  'quotes': ['error', 'single'],
  semi: 'error',
  'semi-spacing': 'error',
  'simple-import-sort/sort': 'error',
  'sort-destructure-keys/sort-destructure-keys': ['error', {
    caseSensitive: true
  }],
  'sort-imports': 'off',
  'sort-imports-es6/sort-imports-es6': ['error', {
    ignoreCase: false,
    ignoreMemberSort: false,
    memberSyntaxSortOrder: ['none', 'all', 'multiple', 'single']
  }],
  'sort-keys': ['error', 'asc', {
    natural: true
  }],
  'space-before-blocks': 'error',
  'space-before-function-paren': ['error', {
    anonymous: 'never',
    named: 'never'
  }],
  'space-in-parens': 'error',
  'space-infix-ops': 'error',
  'space-unary-ops': 'error',
  'spaced-comment': 'error'
};
