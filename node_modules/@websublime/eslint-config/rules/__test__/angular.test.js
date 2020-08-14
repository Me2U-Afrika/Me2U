const path = require('path');
const { createEngine, cleanReport } = require('../../tests/utils');

const configFile = path.resolve(__dirname, '../../angular.js');

describe('Validate Angular ESLint config.', () => {
  /**
   * @typedef { import("eslint").CLIEngine } CLIEngine
   * @type {CLIEngine}
   */
  let engine;

  beforeEach(() => {
    const parserOptions = {
      "ecmaVersion": 6,
      "sourceType": "module",
      "ecmaFeatures": {
        "jsx": true
      }
    };

    engine = createEngine({ configFile, parserOptions });
  });

  it('> Rules: Angular', () => {
    const report = engine.executeOnFiles(["angular.fixture.ts"]);
    expect(cleanReport(report)).toMatchSnapshot();
  })
});
