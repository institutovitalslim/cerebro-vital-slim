import { expect, test, type Locator } from '@playwright/test';
import { readFile } from 'node:fs/promises';

interface GeneratedHook {
  id: string;
  text: string;
  scores: { overall: number };
  compliance: { status: 'pass' | 'review' | 'block' };
}

interface GenerationResponse {
  request_id: string;
  hooks: GeneratedHook[];
}

async function comparableCards(cards: Locator): Promise<Locator[]> {
  const result: Locator[] = [];
  for (let index = 0; index < await cards.count(); index += 1) {
    const card = cards.nth(index);
    if (await card.getByRole('button', { name: 'Comparar', exact: true }).isEnabled()) {
      result.push(card);
    }
  }
  return result;
}

test('jornada real: gera, ranqueia, compara, favorita, consulta e exporta', async ({ page }) => {
  const uniqueTopic = `sono reparador e2e ${Date.now()}`;
  const workspaceReference = `playwright-${Date.now()}`;
  let favoritePosts = 0;

  page.on('request', (request) => {
    if (request.method() === 'POST' && /\/v1\/hooks\/[^/]+\/favorite$/.test(request.url())) {
      favoritePosts += 1;
    }
  });

  await page.goto('/');
  await page.getByLabel('Tema').fill(uniqueTopic);
  await page.getByLabel('Público').fill('adultos com rotina intensa');
  await page.getByLabel('Palavras proibidas').fill('milagre, cura garantida');
  await expect(page.getByLabel('Quantidade')).toHaveValue('12');

  const generationResponsePromise = page.waitForResponse((response) =>
    response.request().method() === 'POST'
      && response.url().includes('/api/backend/v1/hooks/generate'),
  );
  await page.getByRole('button', { name: 'Gerar hooks' }).click();
  const generationResponse = await generationResponsePromise;
  expect(generationResponse.ok()).toBeTruthy();
  const generation = await generationResponse.json() as GenerationResponse;
  expect(generation.hooks).toHaveLength(12);

  const cards = page.locator('section[aria-live="polite"] article');
  await expect(cards).toHaveCount(12);
  await expect(page.getByText(/12 alternativas · motor/)).toBeVisible();

  const visibleScores: number[] = [];
  for (let index = 0; index < 12; index += 1) {
    const card = cards.nth(index);
    await expect(card.getByText('Score geral')).toBeVisible();
    const score = Number(await card.getByText('Score geral').locator('..').locator('strong').innerText());
    visibleScores.push(score);
  }
  expect(visibleScores).toEqual(generation.hooks.map((hook) => Math.round(hook.scores.overall)));
  expect(visibleScores).toEqual([...visibleScores].sort((left, right) => right - left));
  for (const dimension of ['Clareza', 'Especificidade', 'Novidade', 'Retenção', 'Aderência']) {
    await expect(cards.first().getByText(dimension, { exact: true })).toBeVisible();
  }

  const candidates = await comparableCards(cards);
  expect(candidates.length).toBeGreaterThanOrEqual(2);
  const favoriteText = (await candidates[0].locator('blockquote').innerText()).trim();
  await candidates[0].getByRole('button', { name: 'Comparar', exact: true }).click();
  await candidates[1].getByRole('button', { name: 'Comparar', exact: true }).click();
  const comparison = page.getByLabel('Comparação de hooks');
  await expect(comparison.getByText('Comparando 2/3')).toBeVisible();
  await expect(comparison.locator('li')).toHaveCount(2);

  const favoriteResponsePromise = page.waitForResponse((response) =>
    response.request().method() === 'POST'
      && /\/v1\/hooks\/[^/]+\/favorite$/.test(response.url()),
  );
  await candidates[0].getByRole('button', { name: 'Favoritar', exact: true }).evaluate((button) => {
    (button as HTMLButtonElement).click();
    (button as HTMLButtonElement).click();
  });
  expect((await favoriteResponsePromise).ok()).toBeTruthy();
  await expect(candidates[0].getByRole('button', { name: 'Favoritado' })).toBeDisabled();
  await expect.poll(() => favoritePosts).toBe(1);

  await page.getByRole('link', { name: 'Salvos' }).click();
  await expect(page).toHaveURL(/\/saved$/);
  const historyTab = page.getByRole('tab', { name: 'Histórico' });
  const favoritesTab = page.getByRole('tab', { name: 'Favoritos' });
  await expect(historyTab).toHaveAttribute('aria-selected', 'true');
  const session = page.locator('article').filter({
    has: page.getByText(generation.request_id, { exact: true }),
  });
  await expect(session).toBeVisible();
  await expect(session.getByText('12 hooks', { exact: true })).toBeVisible();

  await historyTab.focus();
  await historyTab.press('ArrowRight');
  await expect(favoritesTab).toBeFocused();
  await expect(favoritesTab).toHaveAttribute('aria-selected', 'true');
  await expect(page.getByRole('article', { name: `Hook: ${favoriteText}` })).toBeVisible();

  await favoritesTab.press('Home');
  await expect(historyTab).toBeFocused();
  await expect(historyTab).toHaveAttribute('aria-selected', 'true');
  await expect(session).toBeVisible();
  await page.getByLabel('Referência do workspace').fill(workspaceReference);

  const downloadPromise = page.waitForEvent('download');
  await session.getByRole('button', { name: 'Baixar JSON' }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^hooks-playwright-\d+-[\w-]{1,8}\.json$/);
  const path = await download.path();
  expect(path).not.toBeNull();
  const exported = JSON.parse(await readFile(path!, 'utf8')) as {
    schema_version: string;
    workspace_ref: string;
    hooks: GeneratedHook[];
  };
  expect(exported.schema_version).toBe('1.0.0');
  expect(exported.workspace_ref).toBe(workspaceReference);
  const expectedExportedHooks = generation.hooks.filter(
    (hook) => hook.compliance.status !== 'block',
  );
  expect(exported.hooks).toHaveLength(expectedExportedHooks.length);
  expect(exported.hooks.map((hook) => ({ id: hook.id, text: hook.text }))).toEqual(
    expectedExportedHooks.map((hook) => ({ id: hook.id, text: hook.text })),
  );
  expect(exported.hooks.length).toBeGreaterThan(0);
  expect(exported.hooks.every((hook) => hook.compliance.status !== 'block')).toBeTruthy();
  expect(JSON.stringify(exported)).not.toMatch(/"status":"block"/i);
});
