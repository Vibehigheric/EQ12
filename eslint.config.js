// ESLint 9+ Flat Configuration for EQ12
import js from '@eslint/js';

export default [
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2024,
      sourceType: 'module',
      globals: {
        console: 'readonly',
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly'
      }
    },
    rules: {
      "no-unused-vars": "warn",
      "no-console": "off",
      "prefer-const": "error",
      "no-var": "error",
      "object-shorthand": "error",
      "prefer-arrow-callback": "error",
      "prefer-template": "error",
      "template-curly-spacing": "error"
}
  }
];
