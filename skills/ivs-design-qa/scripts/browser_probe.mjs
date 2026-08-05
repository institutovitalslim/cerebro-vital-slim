#!/usr/bin/env node
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright-core';

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i += 2) {
    const key = argv[i];
    const value = argv[i + 1];
    if (!key?.startsWith('--') || value === undefined) throw new Error(`argumento inválido: ${key ?? ''}`);
    args[key.slice(2)] = value;
  }
  if (!args.input || !args['out-dir']) throw new Error('--input e --out-dir são obrigatórios');
  return args;
}

function issue(code, viewport, count = 1) {
  return { code, severity: 'blocker', viewport, count };
}

function startStaticServer(input) {
  const root = path.dirname(input);
  const mime = {
    '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
    '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml', '.woff2': 'font/woff2',
  };
  const server = http.createServer((req, res) => {
    const requestPath = decodeURIComponent(new URL(req.url || '/', 'http://127.0.0.1').pathname);
    if (requestPath === '/favicon.ico') {
      res.writeHead(204).end();
      return;
    }
    const candidate = path.resolve(root, `.${requestPath}`);
    if (candidate !== root && !candidate.startsWith(`${root}${path.sep}`)) {
      res.writeHead(403).end('forbidden');
      return;
    }
    fs.readFile(candidate, (error, data) => {
      if (error) {
        res.writeHead(404).end('not found');
        return;
      }
      res.writeHead(200, { 'Content-Type': mime[path.extname(candidate).toLowerCase()] || 'application/octet-stream' });
      res.end(data);
    });
  });
  return new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', () => {
      const address = server.address();
      resolve({ server, url: `http://127.0.0.1:${address.port}/${encodeURIComponent(path.basename(input))}` });
    });
  });
}

async function inspectViewport(browser, url, outDir, config) {
  const context = await browser.newContext({
    viewport: { width: config.width, height: config.height },
    deviceScaleFactor: 1,
    colorScheme: 'light',
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const consoleWarnings = [];
  const pageErrors = [];
  page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
    if (message.type() === 'warning') consoleWarnings.push(message.text());
  });
  page.on('pageerror', error => pageErrors.push(error.message));

  await page.goto(url, { waitUntil: 'load', timeout: 30000 });
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page.emulateMedia({ reducedMotion: 'reduce' });

  const metrics = await page.evaluate(() => {
    const root = document.documentElement;
    const body = document.body;
    const scrollWidth = Math.max(root?.scrollWidth || 0, body?.scrollWidth || 0);
    const clientWidth = window.innerWidth;
    const brokenImages = Array.from(document.images).filter(img => !img.complete || img.naturalWidth === 0).length;
    return {
      scroll_width: scrollWidth,
      client_width: clientWidth,
      horizontal_overflow: scrollWidth > clientWidth + 1,
      broken_images: brokenImages,
      sections: document.querySelectorAll('section').length,
    };
  });

  const screenshot = path.join(outDir, `${config.name}.png`);
  await page.screenshot({ path: screenshot, fullPage: true, animations: 'disabled' });
  await context.close();

  return {
    name: config.name,
    width: config.width,
    height: config.height,
    screenshot,
    ...metrics,
    console_errors: consoleErrors.length,
    console_warnings: consoleWarnings.length,
    page_errors: pageErrors.length,
  };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const input = path.resolve(args.input);
  const outDir = path.resolve(args['out-dir']);
  if (!fs.statSync(input).isFile()) throw new Error('input não é arquivo');
  fs.mkdirSync(outDir, { recursive: true });
  const executablePath = process.env.CHROMIUM_PATH || '/snap/bin/chromium';
  const { server, url } = await startStaticServer(input);
  const browser = await chromium.launch({ executablePath, headless: true, args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  let viewports;
  try {
    viewports = [];
    for (const config of [
      { name: 'desktop', width: 1440, height: 1000 },
      { name: 'mobile', width: 390, height: 844 },
    ]) {
      viewports.push(await inspectViewport(browser, url, outDir, config));
    }
  } finally {
    await browser.close();
    await new Promise(resolve => server.close(resolve));
  }

  const blockers = [];
  const concerns = [];
  for (const viewport of viewports) {
    if (viewport.horizontal_overflow) blockers.push(issue('horizontal_overflow', viewport.name));
    if (viewport.broken_images) blockers.push(issue('broken_images', viewport.name, viewport.broken_images));
    if (viewport.page_errors) blockers.push(issue('page_error', viewport.name, viewport.page_errors));
    if (viewport.console_errors) blockers.push(issue('console_error', viewport.name, viewport.console_errors));
    if (viewport.console_warnings) concerns.push({ code: 'console_warning', severity: 'concern', viewport: viewport.name, count: viewport.console_warnings });
  }
  const result = { ok: blockers.length === 0, blockers, concerns, viewports };
  process.stdout.write(`${JSON.stringify(result)}\n`);
  process.exitCode = result.ok ? 0 : 2;
}

main().catch(error => {
  process.stderr.write(`IVS_DESIGN_QA_BROWSER_ERROR: ${error.message}\n`);
  process.exitCode = 1;
});
