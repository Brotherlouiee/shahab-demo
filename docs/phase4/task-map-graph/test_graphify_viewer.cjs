/* Run with the repository's Playwright or set PLAYWRIGHT_MODULE to playwright-core. */
const assert = require('node:assert/strict');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '@playwright/test');

async function run(deviceScaleFactor) {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN, headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 950 }, deviceScaleFactor });
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
        // Canvas transforms use backing-store pixels. Playwright clicks use CSS pixels.
        const { clientWidth, clientHeight, width, height } = context.canvas;
        return [
          (matrix.a * x + matrix.e) * clientWidth / width,
          (matrix.d * y + matrix.f) * clientHeight / height,
        ];
      }
      record('clearRect', () => {
        metrics.frames++;
        metrics.nodes = [];
        metrics.edges = [];
      });
      let cursor = null;
      let segments = [];
      record('beginPath', () => { cursor = null; segments = []; });
      record('arc', (context, x, y, radius) => { metrics.nodes.push([...screen(context, x, y), radius]); });
      record('moveTo', (context, x, y) => { cursor = screen(context, x, y); });
      record('lineTo', (context, x, y) => {
        const end = screen(context, x, y);
        if (cursor) segments.push([cursor, end]);
        cursor = end;
      });
      record('stroke', () => { metrics.edges.push(...segments); });
    });
    const path = process.argv[2] || resolve(__dirname, 'task-map-graph.html');
    await page.goto(pathToFileURL(resolve(path)).href);
    await page.evaluate(() => {
      const ready = window.taskMapGraphReady;
      if (typeof ready?.then !== 'function') throw new Error('Viewer readiness promise is missing');
      return ready;
    });
    const graph = await page.locator('#graph-data').evaluate(source => {
      const { nodes, edges } = JSON.parse(source.textContent);
      return {
        nodes: nodes.map(({ id, package_id, node_type }) => [id, { package_id, node_type }]),
        edges: edges.map(({ source, target, origin_graph, relation_type }) =>
          ({ source, target, origin_graph, relation_type })),
      };
    });
    const nodes = new Map(graph.nodes);
    for (const edge of graph.edges) {
      assert.ok(nodes.has(edge.source), `Edge has unknown source node: ${edge.source}`);
      assert.ok(nodes.has(edge.target), `Edge has unknown target node: ${edge.target}`);
    }
    const crossEdges = graph.edges.filter(edge => {
      if (edge.origin_graph === 'current_project_code_graph') return false;
      if (edge.origin_graph === 'task_mapping' || edge.origin_graph === 'decision_scope') return true;
      const source = nodes.get(edge.source), target = nodes.get(edge.target);
      const distinctPackages = source.package_id && target.package_id && source.package_id !== target.package_id;
      if (edge.relation_type === 'contains') return edge.origin_graph === 'new_project_task_graph' && distinctPackages;
      if (edge.origin_graph === 'relation_overlay') {
        return distinctPackages || [source, target].some(node => node.node_type.endsWith('_REFERENCE'));
      }
      return edge.origin_graph === 'new_project_task_graph' && distinctPackages;
    });
    function crossCounts(relation, showDecisions = true) {
      const edges = crossEdges.filter(edge =>
        (!relation || edge.relation_type === relation) &&
        (showDecisions || [edge.source, edge.target].every(id => nodes.get(id).node_type !== 'OPEN_DECISION')));
      return [new Set(edges.flatMap(edge => [edge.source, edge.target])).size, edges.length];
    }
    const fullGraphCounts = [nodes.size, graph.edges.length];
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
    assert.deepEqual(await counts(), fullGraphCounts);
    await changed('relation filter after idle', () => page.selectOption('#relation', 'handoff'));
    await changed('clear relation filter', () => page.selectOption('#relation', ''));
    await changed('Cross-only', () => page.check('#crossOnly'));
    assert.deepEqual(await counts(), crossCounts());
    await changed('Cross-only intersects relation filter', () => page.selectOption('#relation', 'depends_on'));
    assert.deepEqual(await counts(), crossCounts('depends_on'));
    await changed('Cross-only excludes Plan containment edges', () => page.selectOption('#relation', 'contains'));
    assert.deepEqual(await counts(), [0, 0]);
    await changed('Cross-only handoff edges', () => page.selectOption('#relation', 'handoff'));
    assert.deepEqual(await counts(), crossCounts('handoff'));
    await changed('Cross-only and decision filter', async () => {
      await page.selectOption('#relation', '');
      await page.uncheck('#decisions');
    });
    assert.deepEqual(await counts(), crossCounts('', false));
    await changed('reset filters', async () => {
      await page.uncheck('#crossOnly');
      await page.check('#decisions');
    });
    assert.deepEqual(await counts(), fullGraphCounts);

    const search = page.locator('#search');
    await changed('Search highlights Canvas nodes', () => search.fill('TASK:CORE:C05A:004'));
    await changed('Search Enter centers node', () => search.press('Enter'));
    const centered = await page.evaluate(() => {
      const query = document.getElementById('search').value.toLowerCase();
      const graph = JSON.parse(document.getElementById('graph-data').textContent);
      const match = graph.nodes.find(node => node.id.toLowerCase() === query);
      if (!match) return null;
      const matches = window.painted.nodes.filter(([x, y, radius]) =>
        radius > 2 && Math.abs(x - document.getElementById('graph').clientWidth / 2) < 8 &&
        Math.abs(y - document.getElementById('graph').clientHeight / 2) < 8);
      const node = matches.length === 1 && document.getElementById('details').textContent.includes(match.id);
      return Boolean(node);
    });
    assert.ok(centered, 'Enter did not center the matching node');
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
    const segments = await page.evaluate(() => {
      const canvas = document.body.appendChild(document.createElement('canvas'));
      try {
        canvas.style.cssText = 'position:absolute; width:300px; height:150px';
        const context = canvas.getContext('2d');
        const before = window.painted.edges.length;
        context.beginPath();
        context.moveTo(3, 4);
        context.lineTo(7, 8);
        context.lineTo(11, 12);
        context.moveTo(17, 18);
        context.lineTo(21, 22);
        context.stroke();
        return window.painted.edges.slice(before);
      } finally {
        canvas.remove();
      }
    });
    assert.deepEqual(segments, [[[3, 4], [7, 8]], [[7, 8], [11, 12]], [[17, 18], [21, 22]]]);
    console.log('Browser', browser.version(), 'DPR', deviceScaleFactor);
  } finally {
    await browser.close();
  }
}

run(1).then(() => run(2)).catch(error => { console.error(error); process.exitCode = 1; });
