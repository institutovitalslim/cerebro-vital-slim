import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: { environment: 'jsdom', setupFiles: ['./tests/setup.ts'], css: true },
  resolve: { alias: { '@': import.meta.dirname } },
});
