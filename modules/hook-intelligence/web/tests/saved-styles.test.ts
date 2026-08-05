import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, test } from 'vitest';

const appRoot = resolve(process.cwd(), 'app/saved');

describe('estilos da página Salvos', () => {
  test('o CSS Module declara localmente todas as classes usadas pela página', () => {
    const page = readFileSync(resolve(appRoot, 'page.tsx'), 'utf8');
    const css = readFileSync(resolve(appRoot, 'page.module.css'), 'utf8');
    const usedClasses = [...page.matchAll(/styles\.([A-Za-z][\w-]*)/g)].map(
      ([, className]) => className,
    );

    expect(css).not.toMatch(/@import\s+['"]\.\.\/library\/page\.module\.css['"]/);
    expect(usedClasses.length).toBeGreaterThan(0);

    for (const className of new Set(usedClasses)) {
      expect(css, `classe local ausente: .${className}`).toMatch(
        new RegExp(`(^|[},\\s])\\.${className}(?=[\\s,{.:#>+~\\[])`, 'm'),
      );
    }
  });
});
