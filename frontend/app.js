/* Antidote Dashboard — Frontend logic */

const API = '/api';

// ── Health check ──────────────────────────────────────────────
async function checkHealth() {
    try {
        const res = await fetch(`${API}/health`);
        const data = await res.json();
        const dot = document.getElementById('health-dot');
        const text = document.getElementById('health-text');

        if (data.status === 'healthy') {
            dot.className = 'w-2 h-2 rounded-full bg-green-500';
            text.textContent = `Healthy — v${data.version}`;
            text.className = 'text-green-500 text-sm';
        } else {
            dot.className = 'w-2 h-2 rounded-full bg-yellow-500';
            text.textContent = 'Degraded';
            text.className = 'text-yellow-500 text-sm';
        }
    } catch {
        document.getElementById('health-dot').className = 'w-2 h-2 rounded-full bg-red-500';
        document.getElementById('health-text').textContent = 'Offline';
        document.getElementById('health-text').className = 'text-red-500 text-sm';
    }
}

// ── AI Status ─────────────────────────────────────────────────
async function loadAIStatus() {
    try {
        const res = await fetch(`${API}/ai/status`);
        const data = await res.json();
        const el = document.getElementById('ai-status');

        const mlxBadge = data.mlx.available
            ? '<span class="text-green-400">Available</span>'
            : '<span class="text-red-400">Unavailable</span>';
        const ollamaBadge = data.ollama.available
            ? '<span class="text-green-400">Available</span>'
            : '<span class="text-red-400">Unavailable</span>';

        el.innerHTML = `
            <div class="space-y-2">
                <div class="flex justify-between"><span class="text-gray-400">Backend Config</span><span class="font-mono">${data.backend_config}</span></div>
                <div class="flex justify-between"><span class="text-gray-400">MLX</span><span>${mlxBadge} — <span class="font-mono text-xs">${data.mlx.model}</span></span></div>
                <div class="flex justify-between"><span class="text-gray-400">Ollama</span><span>${ollamaBadge} — <span class="font-mono text-xs">${data.ollama.model}</span></span></div>
            </div>
            <div class="space-y-2">
                <div class="flex justify-between"><span class="text-gray-400">Total Requests</span><span class="font-mono">${data.metrics.total_requests}</span></div>
                <div class="flex justify-between"><span class="text-gray-400">Avg Latency</span><span class="font-mono">${data.metrics.avg_latency_ms}ms</span></div>
                <div class="flex justify-between"><span class="text-gray-400">Last Backend</span><span class="font-mono">${data.metrics.last_backend_used || '—'}</span></div>
                <div class="flex justify-between"><span class="text-gray-400">Failures</span><span class="font-mono">${data.metrics.total_failures}</span></div>
            </div>
        `;

        // Update stats cards
        document.getElementById('stat-backend').textContent = data.metrics.last_backend_used || data.backend_config;
        document.getElementById('stat-latency').textContent = data.metrics.avg_latency_ms ? `${data.metrics.avg_latency_ms}ms` : '—';
    } catch {
        document.getElementById('ai-status').innerHTML = '<div class="text-red-400">Failed to load AI status</div>';
    }
}

// ── Scan ──────────────────────────────────────────────────────
async function runScan() {
    const target = document.getElementById('scan-target').value.trim();
    if (!target) return;

    const btn = document.getElementById('scan-btn');
    const status = document.getElementById('scan-status');

    btn.disabled = true;
    btn.innerHTML = '<span class="scan-spinner"></span>';
    status.classList.remove('hidden');
    status.textContent = 'Scanning...';

    try {
        const res = await fetch(`${API}/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Scan failed');
        }

        const data = await res.json();

        status.textContent = `Scan ${data.scan_id}: ${data.files_scanned} files scanned, ${data.total_findings} finding(s)`;
        status.className = 'mt-3 text-sm text-proof-500';

        document.getElementById('stat-findings').textContent = data.total_findings;
        document.getElementById('stat-files').textContent = data.files_scanned;

        await loadFindings();
        await loadAIStatus();
    } catch (err) {
        status.textContent = `Error: ${err.message}`;
        status.className = 'mt-3 text-sm text-red-400';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Scan';
    }
}

// ── Findings ──────────────────────────────────────────────────
async function loadFindings() {
    try {
        const res = await fetch(`${API}/findings`);
        const data = await res.json();
        const body = document.getElementById('findings-body');

        if (!data.findings.length) {
            body.innerHTML = '<div class="px-6 py-12 text-center text-gray-600 text-sm">No findings yet. Run a scan to get started.</div>';
            document.getElementById('stat-findings').textContent = '0';
            return;
        }

        document.getElementById('stat-findings').textContent = data.total;

        body.innerHTML = data.findings.map(f => `
            <div class="finding-row px-6 py-4 flex items-center justify-between hover:bg-surface-700/50 transition cursor-pointer"
                 onclick="viewPatch('${f._event_file}', '${f.function}')">
                <div class="flex items-center gap-4">
                    <span class="severity-critical">${f.severity}</span>
                    <div>
                        <p class="font-mono text-sm">${f.function}</p>
                        <p class="text-xs text-gray-500">${f.file}:${f.line} &mdash; ${f.rule}</p>
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-xs text-gray-500">${new Date(f.timestamp).toLocaleString()}</p>
                    <p class="text-xs text-proof-500 mt-1">View Patch &rarr;</p>
                </div>
            </div>
        `).join('');
    } catch {
        document.getElementById('findings-body').innerHTML =
            '<div class="px-6 py-8 text-center text-red-400 text-sm">Failed to load findings</div>';
    }
}

// ── Patch viewer ──────────────────────────────────────────────
async function viewPatch(filename, funcName) {
    try {
        const res = await fetch(`${API}/findings/${filename}`);
        const data = await res.json();

        document.getElementById('patch-title').textContent = `Patch: ${funcName}`;
        document.getElementById('patch-content').textContent = data.patch || '(no patch generated)';
        document.getElementById('patch-modal').classList.remove('hidden');
        document.getElementById('patch-modal').classList.add('flex');
    } catch {
        alert('Failed to load patch');
    }
}

function closePatch(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('patch-modal').classList.add('hidden');
    document.getElementById('patch-modal').classList.remove('flex');
}

// ── Keyboard shortcuts ───────────────────────────────────────
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePatch();
    if (e.key === 'Enter' && e.target.id === 'scan-target') runScan();
});

// ── Init ──────────────────────────────────────────────────────
checkHealth();
loadAIStatus();
loadFindings();

// Poll health every 30s
setInterval(checkHealth, 30000);
