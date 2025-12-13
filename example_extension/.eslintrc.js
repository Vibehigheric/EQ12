module.exports = {
  // Extend recommended ESLint configuration for WebExtensions
  extends: [
    'eslint:recommended'
  ],
  
  env: {
    browser: true,
    es2022: true,
    webextensions: true
  },
  
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module'
  },
  
  globals: {
    // Browser API globals
    browser: 'readonly',
    chrome: 'readonly',
    
    // Extension-specific globals
    EQ12Debug: 'writable',
    EQ12Analyzer: 'writable',
    api: 'writable',
    
    // Console globals (for debugging)
    console: 'readonly'
  },
  
  rules: {
    // Mozilla recommended rules for add-ons
    'no-unused-vars': ['error', { 
      'varsIgnorePattern': '^(browser|chrome)$',
      'argsIgnorePattern': '^_'
    }],
    'no-undef': 'error',
    'no-console': 'off', // Allow console for debugging
    'prefer-const': 'error',
    'no-var': 'error',
    
    // Security rules (Mozilla Policy Compliance)
    'no-eval': 'error',
    'no-implied-eval': 'error',
    'no-new-func': 'error',
    'no-script-url': 'error',
    
    // Code quality rules
    'eqeqeq': 'error',
    'curly': 'error',
    'no-multiple-empty-lines': ['error', { 'max': 2 }],
    'semi': ['error', 'always'],
    'quotes': ['error', 'single', { 'allowTemplateLiterals': true }],
    
    // Async/Promise rules
    'no-async-promise-executor': 'error',
    'no-await-in-loop': 'warn',
    'prefer-promise-reject-errors': 'error'
  },
  
  overrides: [
    {
      // Specific rules for background scripts
      files: ['background.js'],
      rules: {
        'no-restricted-globals': ['error', 'window', 'document']
      }
    },
    {
      // Specific rules for content scripts
      files: ['content.js'],
      globals: {
        'window': 'readonly',
        'document': 'readonly',
        'location': 'readonly'
      }
    },
    {
      // Specific rules for popup scripts
      files: ['popup.js'],
      globals: {
        'window': 'readonly',
        'document': 'readonly'
      }
    }
  ]
};