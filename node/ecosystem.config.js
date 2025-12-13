module.exports = {
  apps: [{
    name: 'eq12-realtime',
    script: './server.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      NODE_PORT: 3000
    },
    error_file: '../logs/node_errors.log',
    out_file: '../logs/node_output.log',
    log_file: '../logs/node_combined.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
  }]
};
