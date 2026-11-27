/* Run with the repository's Playwright or set PLAYWRIGHT_MODULE to playwright-core. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { resolve } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '@playwright/test');

async function run(deviceScaleFactor, fixturePath, hostileNodes) {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN, headless: true });
  try {
    const page = await browser.newPage({ viewport: { width: 1500, height: 950 }, deviceScaleFactor });
    const pageErrors = [];
    const consoleErrors = [];
    page.on('pageerror', error => pageErrors.push(error.message));
    page.on('console', message => {
      if (message.type() === 'error') consoleErrors.push(message.text());
    });
    await page.addInitScript(() => {
      window.unhandledRejections = [];
      window.xssExecuted = false;
      window.addEventListener('unhandledrejection', event => window.unhandledRejections.push(String(event.reason)));
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
    await page.goto(pathToFileURL(resolve(fixturePath)).href);
    await page.evaluate(() => {
      const ready = window.taskMapGraphReady;
      if (typeof ready?.then !== 'function') throw new Error('Viewer readiness promise is missing');
      return ready;
    });
    const graph = await page.locator('#graph-data').evaluate(source => {
      const { nodes, edges } = JSON.parse(source.textContent);
      return {
        nodes: nodes.map(node => [node.id, {
          package_id: node.package_id,
          mapped_package_refs: node.mapped_package_refs,
          domain: node.domain,
          community_id: node.community_id,
          node_type: node.node_type,
          mapping_status: node.mapping_status,
          mapping_statuses: node.mapping_statuses,
          label: node.label,
        }]),
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
      if (edge.origin_graph === 'task_mapping' || edge.origin_graph === 'decision_scope') return true;
      if (!['relation_overlay', 'new_project_task_graph'].includes(edge.origin_graph)) return false;
      if (edge.relation_type === 'contains') return false;
      const source = nodes.get(edge.source), target = nodes.get(edge.target);
      const distinctPackages = source.package_id && target.package_id && source.package_id !== target.package_id;
      if (edge.origin_graph === 'relation_overlay') {
        return distinctPackages || [source, target].some(node => node.node_type.endsWith('_REFERENCE'));
      }
      return edge.origin_graph === 'new_project_task_graph' && distinctPackages;
    });
    function expectedCounts(filters = {}) {
      let expectedNodes = graph.nodes.map(([id, node]) => ({ id, ...node })).filter(node => {
        if (filters.domain && node.domain !== filters.domain) return false;
        if (filters.package && node.package_id !== filters.package &&
            !(node.mapped_package_refs || []).includes('PACKAGE:' + filters.package) && node.id !== 'PACKAGE:' + filters.package) return false;
        if (filters.community && node.community_id !== filters.community) return false;
        if (filters.nodeType && node.node_type !== filters.nodeType) return false;
        if (filters.mapping && node.mapping_status !== filters.mapping &&
            !(node.mapping_statuses || []).includes(filters.mapping)) return false;
        if (filters.showDecisions === false && node.node_type === 'OPEN_DECISION') return false;
        return true;
      });
      const eligible = new Set(expectedNodes.map(node => node.id));
      let expectedEdges = graph.edges.filter(edge => eligible.has(edge.source) && eligible.has(edge.target) &&
        (!filters.relation || edge.relation_type === filters.relation) &&
        (!filters.crossOnly || crossEdges.includes(edge)));
      if (filters.crossOnly) {
        const endpoints = new Set(expectedEdges.flatMap(edge => [edge.source, edge.target]));
        expectedNodes = expectedNodes.filter(node => endpoints.has(node.id));
      }
      return [expectedNodes.length, expectedEdges.length];
    }
    const fullGraphCounts = [nodes.size, graph.edges.length];
    const settle = () => page.evaluate(async () => {
      for (let i = 0; i < 5; i++) await new Promise(requestAnimationFrame);
    });
    const bitmap = () => page.locator('#graph').evaluate(canvas => canvas.toDataURL());
    const frames = () => page.evaluate(() => window.painted.frames);
    const counts = () => page.evaluate(() => [window.painted.nodes.length, window.painted.edges.length]);
    const assertCounts = async filters => assert.deepEqual(await counts(), expectedCounts(filters));
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
    const redrawn = async (label, action) => {
      await settle();
      const count = await frames();
      await action();
      await settle();
      assert.ok(await frames() > count, label + ' did not redraw');
      console.log('PASS', label);
    };
    await settle();
    const initial = await frames();
    assert.ok(initial > 0);
    await settle();
    assert.equal(await frames(), initial, 'Canvas kept repainting while idle');
    await page.waitForTimeout(1500);
    assert.equal(await frames(), initial, 'Canvas kept repainting during extended idle');
    assert.deepEqual(await counts(), fullGraphCounts);
    await assertCounts();
    for (const hostile of hostileNodes) {
      await page.locator('#search').fill(hostile.id);
      await page.locator('#search').press('Enter');
      await settle();
      assert.equal(await page.locator('#details h3').textContent(), hostile.label);
      const sourceEvidence = JSON.parse(await page.locator('#details pre').textContent());
      assert.equal(sourceEvidence.source_data.payload, hostile.source_data.payload);
      assert.equal(await page.locator('#details img, #details svg, #details iframe, #details script').count(), 0);
      assert.equal(await page.locator('#details a[href^="javascript:"]').count(), 0);
      assert.equal(await page.evaluate(() => window.xssExecuted), false);
      assert.equal(await page.locator('script').count(), 2);
    }
    await page.locator('#search').fill('');
    await settle();
    await assertCounts();
    await changed('relation filter after idle', () => page.selectOption('#relation', 'handoff'));
    await assertCounts({ relation: 'handoff' });
    await changed('clear relation filter', () => page.selectOption('#relation', ''));
    await assertCounts();
    const selectedCrossNode = crossEdges[0]?.source;
    assert.ok(selectedCrossNode, 'Fixture has no cross-only edge to preserve');
    await page.locator('#search').fill(selectedCrossNode);
    await page.locator('#search').press('Enter');
    await settle();
    assert.match(await page.locator('#details').textContent(), new RegExp(selectedCrossNode.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    await changed('Cross-only preserves visible node selection', () => page.check('#crossOnly'));
    await assertCounts({ crossOnly: true });
    assert.match(await page.locator('#details').textContent(), new RegExp(selectedCrossNode.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    await page.click('#clear');
    await changed('Cross-only intersects relation filter', () => page.selectOption('#relation', 'depends_on'));
    await assertCounts({ crossOnly: true, relation: 'depends_on' });
    await changed('Cross-only containment filter', () => page.selectOption('#relation', 'contains'));
    await assertCounts({ crossOnly: true, relation: 'contains' });
    await changed('Cross-only handoff edges', () => page.selectOption('#relation', 'handoff'));
    await assertCounts({ crossOnly: true, relation: 'handoff' });
    await changed('Cross-only and decision filter', async () => {
      await page.selectOption('#relation', '');
      await page.uncheck('#decisions');
    });
    await assertCounts({ crossOnly: true, showDecisions: false });
    await changed('reset filters', async () => {
      await page.uncheck('#crossOnly');
      await page.check('#decisions');
    });
    assert.deepEqual(await counts(), fullGraphCounts);

    const domain = graph.nodes.map(([, node]) => node.domain).find(value => value === 'CORE');
    const community = graph.nodes.map(([, node]) => node.community_id).find(Boolean);
    await redrawn('Domain filter', () => page.selectOption('#domain', domain));
    await assertCounts({ domain });
    await redrawn('Package filter', () => page.selectOption('#package', 'C05A'));
    await assertCounts({ domain, package: 'C05A' });
    await redrawn('Domain and Package order reset', async () => {
      await page.selectOption('#domain', '');
      await page.selectOption('#package', '');
    });
    await redrawn('Package then Domain', async () => {
      await page.selectOption('#package', 'C05A');
      await page.selectOption('#domain', domain);
    });
    await assertCounts({ domain, package: 'C05A' });
    await redrawn('Incompatible Domain and Package filters', () => page.selectOption('#domain', 'RAG'));
    await assertCounts({ domain: 'RAG', package: 'C05A' });
    await redrawn('Reset Domain and Package', async () => {
      await page.selectOption('#domain', '');
      await page.selectOption('#package', '');
    });
    await redrawn('Community filter', () => page.selectOption('#community', community));
    await assertCounts({ community });
    await redrawn('Community and Relation filters', () => page.selectOption('#relation', 'calls'));
    await assertCounts({ community, relation: 'calls' });
    await redrawn('Reset Community and Relation', async () => {
      await page.selectOption('#community', '');
      await page.selectOption('#relation', '');
    });
    await redrawn('Node Type filter', () => page.selectOption('#nodeType', 'TASK'));
    await assertCounts({ nodeType: 'TASK' });
    await redrawn('Package and Node Type filters', () => page.selectOption('#package', 'C05A'));
    await assertCounts({ nodeType: 'TASK', package: 'C05A' });
    await redrawn('Reset Package and Node Type', async () => {
      await page.selectOption('#package', '');
      await page.selectOption('#nodeType', '');
    });
    await redrawn('Mapping Status filter', () => page.selectOption('#mapping', 'MAPPED'));
    await assertCounts({ mapping: 'MAPPED' });
    await redrawn('Package and Mapping Status filters', () => page.selectOption('#package', 'C05A'));
    await assertCounts({ mapping: 'MAPPED', package: 'C05A' });
    await redrawn('Cross-only and Package filters', () => page.check('#crossOnly'));
    await assertCounts({ crossOnly: true, mapping: 'MAPPED', package: 'C05A' });
    await redrawn('Cross-only and Domain filters', async () => {
      await page.selectOption('#package', '');
      await page.selectOption('#domain', domain);
    });
    await assertCounts({ crossOnly: true, mapping: 'MAPPED', domain });
    await redrawn('Cross-only and Mapping Status filters', async () => {
      await page.selectOption('#domain', '');
      await page.selectOption('#mapping', 'PARTIALLY_MAPPED');
    });
    await assertCounts({ crossOnly: true, mapping: 'PARTIALLY_MAPPED' });
    await redrawn('Cross-only, Mapping Status, and Open Decision filters', () => page.uncheck('#decisions'));
    await assertCounts({ crossOnly: true, mapping: 'PARTIALLY_MAPPED', showDecisions: false });
    await redrawn('Reset all filters', async () => {
      for (const id of ['domain', 'package', 'community', 'nodeType', 'relation', 'mapping']) {
        await page.selectOption('#' + id, '');
      }
      await page.uncheck('#crossOnly');
      await page.check('#decisions');
    });
    await assertCounts();

    const search = page.locator('#search');
    const emptyQueryDetails = await page.locator('#details').textContent();
    await search.fill('');
    await search.press('Enter');
    await settle();
    assert.equal(await page.locator('#details').textContent(), emptyQueryDetails, 'Empty Enter changed the current selection');
    await changed('Search with no matches', () => search.fill('NO-SUCH-TASK-MATCH-9F2C'));
    await assertCounts();
    await search.press('Enter');
    await settle();
    assert.equal(await page.locator('#details pre').count(), 0, 'Empty search selected a node');
    await search.fill('TASK:CORE:C05A');
    await search.press('Enter');
    await settle();
    assert.equal(await page.locator('#details pre').count(), 0, 'Ambiguous search selected a node');
    await search.fill('NO-SUCH-TASK-MATCH-9F2C');
    await changed('Clear empty search', () => search.fill(''));
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
    const targetLabel = nodes.get('TASK:CORE:C05A:004').label;
    assert.ok(targetLabel, 'Target Task fixture has no label');
    assert.equal(graph.nodes.filter(([, node]) => node.label === targetLabel).length, 1, 'Target label is not unique');
    await changed('Search highlights node label', () => search.fill(targetLabel));
    await redrawn('Enter selects exact node label', () => search.press('Enter'));
    assert.match(await page.locator('#details').textContent(), /TASK:CORE:C05A:004/);
    await changed('Package filter clears a hidden node selection', () => page.selectOption('#package', 'A01'));
    assert.doesNotMatch(await page.locator('#details').textContent(), /TASK:CORE:C05A:004/);
    assert.equal(await page.locator('#details pre').count(), 0);
    await changed('Clear package filter', () => page.selectOption('#package', ''));
    const canvas = await page.locator('#graph').boundingBox();
    await changed('Canvas node selection', () => page.mouse.click(canvas.x + canvas.width / 2, canvas.y + canvas.height / 2));
    assert.match(await page.locator('#details').textContent(), /TASK:CORE:C05A:004/);
    await changed('clear node selection', () => page.click('#clear'));
    assert.equal(await page.locator('#details pre').count(), 0);
    const blankPoint = await page.evaluate(({ width, height }) => {
      const { nodes, edges } = window.painted;
      function distance(x, y, [[ax, ay], [bx, by]]) {
        const dx = bx - ax, dy = by - ay;
        const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy || 1)));
        return Math.hypot(x - ax - dx * t, y - ay - dy * t);
      }
      for (let y = 15; y < height - 15; y += 17) {
        for (let x = 15; x < width - 15; x += 19) {
          if (nodes.some(([nx, ny, radius]) => Math.hypot(nx - x, ny - y) < radius + 8)) continue;
          if (edges.some(edge => distance(x, y, edge) < 8)) continue;
          return { x, y };
        }
      }
      return null;
    }, await page.locator('#graph').evaluate(canvas => ({ width: canvas.clientWidth, height: canvas.clientHeight })));
    assert.ok(blankPoint, 'No empty canvas point available for selection-clear check');
    await page.mouse.click(canvas.x + blankPoint.x, canvas.y + blankPoint.y);
    await settle();
    assert.equal(await page.locator('#details pre').count(), 0, 'Empty canvas click selected an item');
    await changed('Canvas pan', async () => {
      const beforeIdleMove = await frames();
      await page.mouse.move(canvas.x + 90, canvas.y + 90);
      await settle();
      assert.equal(await frames(), beforeIdleMove, 'Pointer move without dragging repainted the Canvas');
      await page.mouse.down();
      await page.mouse.move(canvas.x + 91, canvas.y + 91);
      await page.mouse.up();
      await settle();
      await page.mouse.down();
      await page.mouse.move(canvas.x + 160, canvas.y + 125, { steps: 6 });
      await page.mouse.up();
    });
    await changed('Canvas wheel zoom', () => page.mouse.wheel(0, -100));
    await changed('Canvas wheel zoom out', () => page.mouse.wheel(0, 100));
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
    await changed('Cross-only toggle preserves visible edge selection', () => page.uncheck('#crossOnly'));
    evidence = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(evidence.relation_type, 'requires_contract');
    await changed('Restore Cross-only edge selection', () => page.check('#crossOnly'));
    await changed('Relation filter clears a hidden edge selection', () => page.selectOption('#relation', 'handoff'));
    assert.equal(await page.locator('#details pre').count(), 0);
    assert.doesNotMatch(await page.locator('#details').textContent(), /REL-STAGE4-/);
    const decisionId = graph.nodes.find(([, node]) => node.node_type === 'OPEN_DECISION')[0];
    await changed('Open Decision source and mapping details', async () => {
      await page.selectOption('#relation', '');
      await page.uncheck('#crossOnly');
      await search.fill(decisionId);
      await search.press('Enter');
    });
    const decisionDetails = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(decisionDetails.decision_status, 'OPEN');
    assert.equal(decisionDetails.mapping_status, 'BLOCKED');
    await changed('Decision toggle clears hidden decision selection', () => page.uncheck('#decisions'));
    assert.equal(await page.locator('#details pre').count(), 0);
    await page.check('#decisions');
    const contractId = graph.nodes.find(([, node]) => node.node_type === 'CONTRACT_REFERENCE')[0];
    await changed('Contract source reference details', async () => {
      await search.fill(contractId);
      await search.press('Enter');
    });
    const contractDetails = JSON.parse(await page.locator('#details pre').textContent());
    assert.ok(contractDetails.source_data);
    assert.equal(contractDetails.source_data.canonical_reference, contractId);
    await search.fill('COVERAGE:HUB');
    await search.press('Enter');
    await settle();
    const hubDetails = await page.locator('#details').textContent();
    assert.match(hubDetails, /COVERAGE:HUB/);
    assert.match(hubDetails, /برای کارایی فقط ۲۵۰ مورد نخست نمایش داده شده است/);
    const hubEvidence = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(hubEvidence.source_data, null);
    await changed('Synthetic edge source fallback setup', async () => {
      await page.selectOption('#domain', 'COVERAGE_SINGLE');
      await page.selectOption('#relation', 'coverage_single');
      await page.click('#fit');
    });
    const syntheticEdgePoint = await page.evaluate(() => {
      const [[ax, ay], [bx, by]] = window.painted.edges[0] || [];
      if (![ax, ay, bx, by].every(Number.isFinite)) return null;
      for (const fraction of [0.5, 0.25, 0.75]) {
        const x = Math.round(ax + (bx - ax) * fraction), y = Math.round(ay + (by - ay) * fraction);
        if (!window.painted.nodes.some(([nx, ny]) => Math.hypot(nx - x, ny - y) < 10)) return { x, y };
      }
      return null;
    });
    assert.ok(syntheticEdgePoint,
      'Synthetic fixture edge was not drawn: ' + JSON.stringify(await page.evaluate(() => ({
        relation: document.getElementById('relation').value,
        crossOnly: document.getElementById('crossOnly').checked,
        edges: window.painted.edges.length,
        graphEdges: JSON.parse(document.getElementById('graph-data').textContent).edges.filter(edge => edge.relation_type === 'coverage_single').length,
      }))));
    const syntheticBounds = await page.locator('#graph').boundingBox();
    await page.mouse.click(syntheticBounds.x + syntheticEdgePoint.x, syntheticBounds.y + syntheticEdgePoint.y);
    await settle();
    const syntheticEdgeDetails = JSON.parse(await page.locator('#details pre').textContent());
    assert.equal(syntheticEdgeDetails.relation_type, 'coverage_single');
    assert.equal(syntheticEdgeDetails.relation_id, 'COVERAGE:EDGE');
    assert.equal(syntheticEdgeDetails.source_refs[0], 'fixture-only');
    assert.deepEqual(pageErrors, []);
    assert.deepEqual(consoleErrors, []);
    assert.deepEqual(await page.evaluate(() => window.unhandledRejections), []);
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

function makeSecurityFixture(sourcePath) {
  const html = fs.readFileSync(sourcePath, 'utf8');
  const match = html.match(/(<script id="graph-data" type="application\/json">)([\s\S]*?)(<\/script>)/);
  assert.ok(match, 'Standalone graph JSON script was not found');
  const graph = JSON.parse(match[2]);
  const unclusteredCode = graph.nodes.find(node => node.node_type === 'CODE');
  assert.ok(unclusteredCode, 'Code node is required to test the optional community fallback');
  unclusteredCode.community_id = null;
  const payloads = [
    '<img src=x onerror="window.xssExecuted=true">',
    '</script><script>window.xssExecuted=true</script>',
    '"><svg onload="window.xssExecuted=true">',
    "'><iframe src=javascript:window.xssExecuted=true>",
    'javascript:alert(1)',
    'quote " apostrophe \' ampersand & angle < >',
    'فارسی العربية 日本語 雪 ☃️',
  ];
  const hostileNodes = payloads.map((payload, index) => ({
    id: `XSS:<&"'雪:${index}`,
    canonical_id: `XSS:<&"'雪:${index}`,
    source_id: `XSS:<&"'雪:${index}`,
    node_type: 'CONTRACT_REFERENCE',
    origin_graph: 'relation_overlay_reference',
    label: payload,
    domain: null,
    package_id: null,
    community_id: null,
    mapping_status: null,
    source_data: { payload, source_text: payload, url: 'javascript:alert(1)' },
  }));
  hostileNodes[0].source_ref = { artifact: 'missing-snapshot', collection: 'nodes', index: 0 };
  hostileNodes[1].source_ref = { artifact: 'task_map_mapping', collection: '', index: 0 };
  const hub = {
    id: 'COVERAGE:HUB', canonical_id: 'COVERAGE:HUB', source_id: 'COVERAGE:HUB',
    node_type: 'UNCLASSIFIED', label: null, domain: 'COVERAGE_SINGLE', package_id: null,
    community_id: null, mapping_status: null, source_data: null,
  };
  const neighbors = Array.from({ length: 251 }, (_, index) => ({
    id: `COVERAGE:NEIGHBOR:${index}`, canonical_id: `COVERAGE:NEIGHBOR:${index}`,
    source_id: `COVERAGE:NEIGHBOR:${index}`, node_type: 'UNCLASSIFIED', label: null,
    domain: index === 0 ? 'COVERAGE_SINGLE' : 'COVERAGE_OTHER',
    package_id: null, community_id: null, mapping_status: null,
  }));
  const fallbackPackage = {
    id: 'PACKAGE:COVERAGE', canonical_id: 'PACKAGE:COVERAGE', source_id: 'PACKAGE:COVERAGE',
    node_type: 'PACKAGE', label: 'Coverage package', domain: 'COVERAGE_PACKAGE',
    package_id: 'COVERAGE', community_id: null, mapping_status: 'NEW_IMPLEMENTATION',
  };
  const fallbackTask = {
    id: 'TASK:COVERAGE:FALLBACK', canonical_id: 'TASK:COVERAGE:FALLBACK',
    source_id: 'TASK:COVERAGE:FALLBACK', node_type: 'TASK', label: 'Fallback task',
    domain: 'COVERAGE_PACKAGE', package_id: null, parent_id: fallbackPackage.id,
    community_id: null, mapping_status: 'NEW_IMPLEMENTATION', source_data: null,
  };
  const fallbackSubtask = {
    id: 'SUBTASK:COVERAGE:FALLBACK', canonical_id: 'SUBTASK:COVERAGE:FALLBACK',
    source_id: 'SUBTASK:COVERAGE:FALLBACK', node_type: 'SUBTASK', label: 'Fallback subtask',
    domain: 'COVERAGE_PACKAGE', package_id: null, parent_id: 'TASK:CORE:C05A:004',
    community_id: null, mapping_status: 'NEW_IMPLEMENTATION',
  };
  const sourceDataTask = {
    id: 'TASK:COVERAGE:SOURCE-DATA', canonical_id: 'TASK:COVERAGE:SOURCE-DATA',
    source_id: 'TASK:COVERAGE:SOURCE-DATA', node_type: 'TASK', label: 'Source data task',
    domain: 'COVERAGE_PACKAGE', package_id: null, parent_id: 'TASK:CORE:C05A:004',
    community_id: null, mapping_status: 'NEW_IMPLEMENTATION',
    source_data: { package_id: 'COVERAGE' },
  };
  const emptyPackage = {
    id: 'PACKAGE:COVERAGE:EMPTY', canonical_id: 'PACKAGE:COVERAGE:EMPTY',
    source_id: 'PACKAGE:COVERAGE:EMPTY', node_type: 'PACKAGE', label: 'Empty package',
    domain: 'COVERAGE_PACKAGE', package_id: 'COVERAGE:EMPTY', community_id: null,
    mapping_status: 'NEW_IMPLEMENTATION',
  };
  const isolatedDecision = {
    id: 'DECISION:COVERAGE:ISOLATED', canonical_id: 'DECISION:COVERAGE:ISOLATED',
    source_id: 'DECISION:COVERAGE:ISOLATED', node_type: 'OPEN_DECISION',
    label: 'Isolated decision', domain: null, package_id: null, community_id: null,
    decision_status: 'OPEN', mapping_status: 'BLOCKED',
  };
  graph.nodes.push(hub, ...neighbors, fallbackPackage, fallbackTask, fallbackSubtask,
    sourceDataTask, emptyPackage, isolatedDecision, ...hostileNodes);
  graph.edges.push(...neighbors.map((node, index) => ({
    id: `COVERAGE:EDGE:${index}`, source: hub.id, target: node.id,
    origin_graph: 'coverage_fixture', relation_type: index === 0 ? 'coverage_single' : 'coverage_many',
    ...(index === 0 ? { relation_id: 'COVERAGE:EDGE', source_refs: ['fixture-only'] } : {}),
  })));
  graph.counts.node_total = graph.nodes.length;
  graph.counts.edge_total = graph.edges.length;
  graph.counts.nodes.UNCLASSIFIED = (graph.counts.nodes.UNCLASSIFIED || 0) + neighbors.length + 1;
  graph.counts.nodes.PACKAGE++;
  graph.counts.nodes.PACKAGE++;
  graph.counts.nodes.TASK += 2;
  graph.counts.nodes.SUBTASK++;
  graph.counts.nodes.OPEN_DECISION++;
  graph.counts.nodes.CONTRACT_REFERENCE = (graph.counts.nodes.CONTRACT_REFERENCE || 0) + hostileNodes.length;
  const serialized = JSON.stringify(graph).replace(/<\//g, '<\\/');
  const fixture = html.replace(match[0], `${match[1]}${serialized}${match[3]}`);
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'shahab-xss-'));
  const fixturePath = path.join(directory, 'viewer.html');
  fs.writeFileSync(fixturePath, fixture, 'utf8');
  return { directory, fixturePath, hostileNodes };
}

async function runFallbackCases(sourcePath) {
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN, headless: true });
  let fixtureDirectory;
  try {
    const html = fs.readFileSync(sourcePath, 'utf8');
    const match = html.match(/(<script id="graph-data" type="application\/json">)([\s\S]*?)(<\/script>)/);
    assert.ok(match, 'Standalone graph JSON script was not found for fallback tests');
    const graph = JSON.parse(match[2]);
    const nullPayloadHtml = html.replace(match[0], `${match[1]}${JSON.stringify({ ...graph, source_payloads: null })}${match[3]}`);
    fixtureDirectory = fs.mkdtempSync(path.join(os.tmpdir(), 'shahab-viewer-fallback-'));
    const nullPayloadPath = path.join(fixtureDirectory, 'null-payload.html');
    fs.writeFileSync(nullPayloadPath, nullPayloadHtml, 'utf8');
    const page = await browser.newPage({ viewport: { width: 900, height: 700 } });
    await page.addInitScript(() => Object.defineProperty(window, 'devicePixelRatio', { configurable: true, value: 0 }));
    await page.goto(pathToFileURL(nullPayloadPath).href);
    await page.evaluate(() => window.taskMapGraphReady);
    assert.equal(await page.evaluate(() => window.devicePixelRatio), 0, 'Zero-DPR fixture did not set the browser environment');
    const dimensions = await page.locator('#graph').evaluate(canvas => [canvas.width, canvas.clientWidth]);
    assert.deepEqual(dimensions, [Math.max(1, dimensions[1]), dimensions[1]], 'DPR fallback did not use CSS pixel dimensions');
    console.log('PASS empty source payloads and zero-DPR fallback');

    const zlib = require('node:zlib');
    const emptyPayload = { encoding: 'gzip+base64', media_type: 'application/json', data: zlib.gzipSync(Buffer.alloc(0)).toString('base64') };
    const emptyCompressedHtml = html.replace(match[0], `${match[1]}${JSON.stringify({ ...graph, source_payloads: { empty: emptyPayload } })}${match[3]}`);
    const errorPage = await browser.newPage();
    await errorPage.setContent(emptyCompressedHtml);
    await assert.rejects(errorPage.evaluate(() => window.taskMapGraphReady), /Source snapshot decompressed empty/);
    assert.match(await errorPage.locator('#hud').textContent(), /خطا در آماده‌سازی منبع گراف/);
    console.log('PASS empty decompressed snapshot error and HUD reporting');

    const noHudHtml = emptyCompressedHtml.replace(/<div class="hud" id="hud">[\s\S]*?<\/div>/, '');
    const noHudPage = await browser.newPage();
    await noHudPage.setContent(noHudHtml);
    await assert.rejects(noHudPage.evaluate(() => window.taskMapGraphReady), /Source snapshot decompressed empty/);
    console.log('PASS initialization failure without optional HUD');
  } finally {
    await browser.close();
    if (fixtureDirectory) fs.rmSync(fixtureDirectory, { recursive: true, force: true });
  }
}

const sourcePath = process.argv[2] || resolve(__dirname, 'task-map-graph.html');
const securityFixture = makeSecurityFixture(sourcePath);
run(1, securityFixture.fixturePath, securityFixture.hostileNodes)
  .then(() => run(2, securityFixture.fixturePath, securityFixture.hostileNodes))
  .then(() => runFallbackCases(sourcePath))
  .catch(error => { console.error(error); process.exitCode = 1; })
  .finally(() => fs.rmSync(securityFixture.directory, { recursive: true, force: true }));
