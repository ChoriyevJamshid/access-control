import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) {
            return;
          }

          const packagePath = id.split('node_modules/')[1];
          const parts = packagePath.split('/');
          const packageName = parts[0].startsWith('@')
            ? `${parts[0]}/${parts[1]}`
            : parts[0];

          if (['react', 'react-dom', 'scheduler'].includes(packageName)) {
            return 'react-vendor';
          }

          if (packageName === 'antd') {
            return 'antd-core';
          }

          if (packageName === '@ant-design/icons') {
            return 'ant-icons';
          }

          if (packageName.startsWith('rc-')) {
            return `${packageName}-vendor`;
          }

          if (packageName.startsWith('@rc-component/')) {
            return `${packageName.replace('@rc-component/', 'rc-')}-vendor`;
          }

          if (packageName.startsWith('@tanstack/')) {
            return 'query-vendor';
          }

          if (
            packageName === 'recharts' ||
            packageName.startsWith('d3-') ||
            packageName.startsWith('victory-')
          ) {
            return 'charts-vendor';
          }

          if (
            packageName === 'axios' ||
            packageName === 'dayjs' ||
            packageName === 'cookie' ||
            packageName === 'set-cookie-parser' ||
            packageName === 'string-convert' ||
            packageName === 'json2mq'
          ) {
            return 'utils-vendor';
          }

          if (packageName === 'react-router' || packageName === 'react-router-dom') {
            return 'router-vendor';
          }

          return `${packageName.replace('@', '').replace('/', '-')}-vendor`;
        },
      },
    },
  },
})
