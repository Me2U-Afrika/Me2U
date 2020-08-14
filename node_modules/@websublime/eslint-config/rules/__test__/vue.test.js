const path = require('path');
const { createEngine, cleanReport } = require('../../tests/utils');

const configFile = path.resolve(__dirname, '../../vue.js');

describe('Validate Vue ESLint config.', () => {
  /**
   * @typedef { import("eslint").CLIEngine } CLIEngine
   * @type {CLIEngine}
   */
  let engine;

  beforeEach(() => {
    const parserOptions = {
      "parser": "babel-eslint",
      "ecmaVersion": 2017,
      "sourceType": "module"
    };

    engine = createEngine({ configFile, parserOptions });
  });

  it('> Rules: Vuejs', () => {
    const report = engine.executeOnFiles(["vue.fixture.vue"]);
    expect(cleanReport(report)).toMatchSnapshot();
  })
});
