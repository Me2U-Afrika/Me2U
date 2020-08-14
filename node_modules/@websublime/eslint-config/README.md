# eslint-config

These are my personal configurations for [ESLint](https://github.com/eslint/eslint). They are based on [Airbnb's ESLint configurations](https://github.com/airbnb/javascript).

## Overview

This repository contains ESLint configurations for the following setups:

- JavaScript
- JavaScript with React
- TypeScript
- TypeScript with React
- Angular
- Vue

They are designed to be used together with [Prettier](https://github.com/prettier/prettier).

## Usage

1. **Install the required packages:**

   - JavaScript:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb-base
     ```

   - JavaScript with React:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb
     ```

   - TypeScript:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       @typescript-eslint/eslint-plugin \
       @typescript-eslint/parser \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb-base
     ```

   - TypeScript with React:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       @typescript-eslint/eslint-plugin \
       @typescript-eslint/parser \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb
     ```

   - Angular:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       @typescript-eslint/eslint-plugin \
       @typescript-eslint/parser \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb
     ```

   - Vuejs:

     ```sh
     yarn add --dev @websublime/eslint-config \
       eslint-config-prettier \
       eslint-plugin-vue \
       @typescript-eslint/eslint-plugin \
       @typescript-eslint/parser \
       vue-eslint-parser \
       eslint-plugin-simple-import-sort \
       && npx install-peerdeps --dev eslint-config-airbnb
     ```

2. **Create the following entry in your `package.json` file:**

   - JavaScript:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config"]
       }
     }
     ```

   - JavaScript with React:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config/react"]
       }
     }
     ```

   - TypeScript:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config/typescript"]
       }
     }
     ```

   - TypeScript with React:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config/typescript-react"]
       }
     }
     ```

   - Angular:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config/angular"]
       }
     }
     ```

   - Vuejs:

     ```json
     {
       "eslintConfig": {
         "root": true,
         "extends": ["@websublime/eslint-config/vue"]
       }
     }
     ```

3. **Add a linting script to your `package.json` file:**

   - JavaScript:

     ```json
     {
       "scripts": {
         "lint": "eslint --fix --max-warnings 0 ."
       }
     }
     ```

   - JavaScript with React:

     ```json
     {
       "scripts": {
         "lint": "eslint --ext .js,.jsx --fix --max-warnings 0 ."
       }
     }
     ```

   - TypeScript:

     ```json
     {
       "scripts": {
         "lint": "eslint --ext .ts --fix --max-warnings 0 ."
       }
     }
     ```

   - TypeScript with React:

     ```json
     {
       "scripts": {
         "lint": "eslint --ext .ts,.tsx --fix --max-warnings 0 ."
       }
     }
     ```
