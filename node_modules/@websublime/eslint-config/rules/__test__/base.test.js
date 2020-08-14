const path = require('path');
const { createEngine, cleanReport } = require('../../tests/utils');

const configFile = path.resolve(__dirname, '../../index.js');

describe('Validate Base ESLint config.', () => {
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

  it('> Rules: Base', () => {
    const report = engine.executeOnFiles(["base.fixture.jsx"]);
    expect(cleanReport(report)).toMatchSnapshot();
  })
});
