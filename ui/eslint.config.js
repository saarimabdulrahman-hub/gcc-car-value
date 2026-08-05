// Flat config (ESLint 8.57+/9). A project-local config is REQUIRED here because
// a stray ~/eslint.config.js in the home dir otherwise gets picked up by ESLint's
// upward search and forces flat-config mode with no rules. Nearest config wins.
const js = require("@eslint/js");
const react = require("eslint-plugin-react");
const reactHooks = require("eslint-plugin-react-hooks");
const globals = require("globals");
const tsParser = require("@typescript-eslint/parser");

module.exports = [
  { ignores: ["dist/**", "node_modules/**", "assets/**", "react-browse.html", "**/*.config.{js,cjs,mjs,ts}"] },
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: { ecmaFeatures: { jsx: true } },
      globals: { ...globals.browser },
    },
    plugins: { react, "react-hooks": reactHooks },
    settings: { react: { version: "detect" } },
    rules: {
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // TypeScript owns these; the ESLint core versions misfire on TS syntax.
      "no-undef": "off",
      "no-unused-vars": "warn",
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
      // Core rules that flag benign legacy-JS patterns in the hand-written
      // production bundle (js/index.js) — keep them visible, don't block CI.
      "no-redeclare": "warn",
      "no-empty": "warn",
      "no-inner-declarations": "warn",
    },
  },
];
