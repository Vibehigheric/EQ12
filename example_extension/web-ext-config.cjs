// Web-ext Configuration for EQ12 Governance Assistant
module.exports = {
  // Ignore files during build and lint
  ignoreFiles: [
    'node_modules/**',
    '.git/**',
    '.DS_Store',
    '*.log',
    '*.tmp',
    '.env',
    '.env.local',
    '../builds/**',
    '../dist/**',
    '*.zip',
    '*.xpi',
    '.eslintrc.js',
    '.prettierrc',
    'package.json',
    'package-lock.json',
    'README.md',
    'CONTRIBUTING.md',
    'LICENSE',
    'tests/**',
    'test/**',
    'spec/**',
    '.vscode/**',
    '.idea/**',
    '*.swp',
    '*.swo',
    'Thumbs.db',
    'debug-test-page.html',
    'debug-report.json',
    'debug-config.json',
    '*.md'
  ],

  // Build configuration
  build: {
    overwriteDest: true
  },
  
  // Artifacts directory
  artifactsDir: '../builds/web-ext/',

  // Run configuration  
  run: {
    firefox: 'firefox',
    browserConsole: true,
    startUrl: [
      'about:debugging#/runtime/this-firefox'
    ]
  },

  // Lint configuration
  lint: {
    pretty: true,
    metadata: true,
    output: 'text',
    warningsAsErrors: false
  },

  // Note: Sign and submit configuration can be set via command line or environment variables
};