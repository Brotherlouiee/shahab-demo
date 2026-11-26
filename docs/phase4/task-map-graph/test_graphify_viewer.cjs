/* Run with the repository's Playwright or set PLAYWRIGHT_MODULE to playwright-core. */
const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '@playwright/test');

async function run() {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN, headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 950 } });
    const pageErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));
    await page.addInitScript(() => {
      const prototype = CanvasRenderingContext2D.prototype;
      const metrics = window.painted = { frames: 0, nodes: [], edges: [] };
      function record(name, observe) {
        const original = prototype[name];
        prototype[name] = function (...args) {
          observe(this, ...args);
          return original.apply(this, args);
        };
      }
      function screen(context, x, y) {
        const matrix = context.getTransform();
        return [matrix.a * x + matrix.e, matrix.d * y + matrix.f];
      }
      record('clearRect', () => {
        metrics.frames++;
        metrics.nodes = [];
        metrics.edges = [];
      });
      record('beginPath', () => { metrics.start = null; metrics.end = null; });
      record('arc', (context, x, y, radius) => { metrics.nodes.push([...screen(context, x, y), radius]); });
      record('moveTo', (context, x, y) => { metrics.start = screen(context, x, y); });
      record('lineTo', (context, x, y) => { metrics.end = screen(context, x, y); });
      record('stroke', () => {
        if (metrics.start && metrics.end) metrics.edges.push([metrics.start, metrics.end]);
      });
    });
    const path = process.argv[2] || resolve(__dirname, 'task-map-graph.html');
    await page.goto(pathToFileURL(resolve(path)).href);
    await page.evaluate(() => window.taskMapGraphReady);
    const settle = () => page.evaluate(async () => {
      for (let i = 0; i < 5; i++) await new Promise(requestAnimationFrame);
    });
    const bitmap = () => page.locator('#graph').evaluate(canvas => canvas.toDataURL());
    const frames = () => page.evaluate(() => window.painted.frames);
    const counts = () => page.evaluate(() => [window.painted.nodes.length, window.painted.edges.length]);
    const changed = async (label, action) => {
      await settle();
      const before = await bitmap();
      const count = await frames();
      await action();
      await settle();
      assert.ok(await frames() > count, label + ' did not redraw');
      assert.notEqual(await bitmap(), before, label + ' did not change Canvas pixels');
      console.log('PASS', label);
    };
    await settle();
    const initial = await frames();
    assert.ok(initial > 0);
    await settle();
    assert.equal(await frames(), initial, 'Canvas kept repainting while idle');
    await changed('relation filter after idle', () => page.selectOption('#relation', 'handoff'));
    await changed('clear relation filter', () => page.selectOption('#relation', ''));
    await changed('Cross-only', () => page.check('#crossOnly'));
    assert.deepEqual(await counts(), [380, 823]);
    await changed('Cross-only intersects relation filter', () => page.selectOption('#relation', 'depends_on'));
    assert.deepEqual(await counts(), [10, 11]);
    await changed('Cross-only excludes containment edges', () => page.selectOption('#relation', 'contains'));
    assert.deepEqual(await counts(), [0, 0]);
    await changed('Cross-only handoff edges', () => page.selectOption('#relation', 'handoff'));
    assert.equal((await counts())[1], 50);
    await changed('Cross-only and decision filter', async () => {
      await page.selectOption('#relation', '');
      await page.uncheck('#decisions');
    });
    assert.equal((await counts())[1], 206);
    await changed('reset filters', async () => {
      await page.uncheck('#crossOnly');
      await page.check('#decisions');
    });
    assert.deepEqual(await counts(), [4490, 11435]);

    const search = page.locator('#search');
    await changed('Search highlights Canvas nodes', () => search.fill('TASK:CORE:C05A:004'));
    await changed('Search Enter centers node', () => search.press('Enter'));
    let evidence = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(evidence.source_data.id, 'TASK:CORE:C05A:004');
    assert.ok(evidence.mapping_data);
    await changed('clear node selection', () => page.click('#clear'));
    const canvas = await page.locator('#graph').boundingBox();
    await changed('Canvas node selection', () => page.mouse.click(canvas.x + canvas.width / 2, canvas.y + canvas.height / 2));
    assert.match(await page.locator('#details').textContent(), /TASK:CORE:C05A:004/);
    await changed('Canvas pan', async () => {
      await page.mouse.move(canvas.x + 90, canvas.y + 90);
      await page.mouse.down();
      await page.mouse.move(canvas.x + 160, canvas.y + 125, { steps: 6 });
      await page.mouse.up();
    });
    await changed('Canvas wheel zoom', () => page.mouse.wheel(0, -100));
    await changed('Canvas button zoom', () => page.click('#zout'));
    await changed('Fit', () => page.click('#fit'));
    await changed('Resize', () => page.setViewportSize({ width: 1600, height: 1000 }));
    await changed('clear search', () => search.fill(''));
    await changed('edge selection setup', async () => {
      await page.click('#clear');
      await page.check('#crossOnly');
      await page.selectOption('#relation', 'requires_contract');
      await page.click('#fit');
    });
    const bounds = await page.locator('#graph').boundingBox();
    const point = await page.evaluate(({ width, height }) => {
      const { nodes, edges } = window.painted;
      function distance(x, y, [[ax, ay], [bx, by]]) {
        const dx = bx - ax, dy = by - ay;
        const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy || 1)));
        return Math.hypot(x - ax - dx * t, y - ay - dy * t);
      }
      for (const [i, [[ax, ay], [bx, by]]] of edges.entries()) {
        for (const fraction of [0.5, 0.25, 0.75]) {
          const x = Math.round(ax + (bx - ax) * fraction), y = Math.round(ay + (by - ay) * fraction);
          if (x < 10 || x > width - 10 || y < 10 || y > height - 10) continue;
          if (nodes.some(([nx, ny]) => Math.hypot(nx - x, ny - y) < 12)) continue;
          if (edges.some((edge, j) => i !== j && distance(x, y, edge) < 6)) continue;
          return { x, y };
        }
      }
      return null;
    }, bounds);
    assert.ok(point, 'No isolated edge to click');
    await changed('Canvas edge selection', () => page.mouse.click(bounds.x + point.x, bounds.y + point.y));
    evidence = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(evidence.relation_type, 'requires_contract');
    assert.ok(evidence.relation_id && evidence.source_refs.length && evidence.plan_locator);
    console.log('PASS Source Evidence for node and overlay edge');
    assert.deepEqual(pageErrors, []);
    console.log('Browser', browser.version());
  } finally {
    await browser.close();
  }
}

run().catch(error => { console.error(error); process.exitCode = 1; });
