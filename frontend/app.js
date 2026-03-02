/* Antidote — Dashboard logic */

// ── Splash screen ────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const splash = document.getElementById('splash');
    if (splash) {
        setTimeout(() => {
            splash.classList.add('fade-out');
            setTimeout(() => splash.remove(), 500);
        }, 3000);
    }
});

const API = '/api';

// ── Health ────────────────────────────────────────────────────
async function checkHealth() {
    const dot = document.getElementById('health-dot');
    const text = document.getElementById('health-text');
    try {
        const res = await fetch(`${API}/health`);
        const data = await res.json();
        if (data.status === 'healthy') {
            dot.className = 'status-dot ok';
            text.textContent = `v${data.version}`;
        } else {
            dot.className = 'status-dot warn';
            text.textContent = 'Degraded';
        }
    } catch {
        dot.className = 'status-dot err';
        text.textContent = 'Offline';
    }
}

// ── AI Status ─────────────────────────────────────────────────
async function loadAIStatus() {
    try {
        const res = await fetch(`${API}/ai/status`);
        const d = await res.json();
        const el = document.getElementById('ai-status');

        const mlx = d.mlx.available ? `<span class="badge-ok">Active</span>` : `<span class="badge-err">Inactive</span>`;
        const oll = d.ollama.available ? `<span class="badge-ok">Active</span>` : `<span class="badge-err">Inactive</span>`;

        el.innerHTML = `
            <div class="ai-card">
                <div class="ai-card-title">Backends</div>
                <div class="ai-row"><span class="ai-row-label">Config</span><span class="ai-row-value">${d.backend_config}</span></div>
                <div class="ai-row"><span class="ai-row-label">MLX</span><span>${mlx}</span></div>
                <div class="ai-row"><span class="ai-row-label">Ollama</span><span>${oll}</span></div>
            </div>
            <div class="ai-card">
                <div class="ai-card-title">Metrics</div>
                <div class="ai-row"><span class="ai-row-label">Requests</span><span class="ai-row-value">${d.metrics.total_requests}</span></div>
                <div class="ai-row"><span class="ai-row-label">Avg latency</span><span class="ai-row-value">${d.metrics.avg_latency_ms ? d.metrics.avg_latency_ms + 'ms' : '—'}</span></div>
                <div class="ai-row"><span class="ai-row-label">Last used</span><span class="ai-row-value">${d.metrics.last_backend_used || '—'}</span></div>
                <div class="ai-row"><span class="ai-row-label">Failures</span><span class="ai-row-value">${d.metrics.total_failures}</span></div>
            </div>
        `;

        document.getElementById('stat-backend').textContent = d.metrics.last_backend_used || d.backend_config;
        document.getElementById('stat-latency').textContent = d.metrics.avg_latency_ms ? `${d.metrics.avg_latency_ms}ms` : '—';
    } catch {
        document.getElementById('ai-status').innerHTML = '<div class="ai-placeholder">Unable to reach AI backend</div>';
    }
}

// ── Scan ──────────────────────────────────────────────────────
async function runScan() {
    const target = document.getElementById('scan-target').value.trim();
    if (!target) return;

    const btn = document.getElementById('scan-btn');
    const label = btn.querySelector('.btn-label');
    const spinner = btn.querySelector('.btn-spinner');
    const status = document.getElementById('scan-status');

    btn.disabled = true;
    label.classList.add('hidden');
    spinner.classList.remove('hidden');
    status.classList.remove('hidden');
    status.className = 'scan-status';
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
        status.textContent = `${data.files_scanned} file${data.files_scanned !== 1 ? 's' : ''} scanned \u00B7 ${data.total_findings} finding${data.total_findings !== 1 ? 's' : ''}`;
        status.className = 'scan-status ok';

        document.getElementById('stat-findings').textContent = data.total_findings;
        document.getElementById('stat-files').textContent = data.files_scanned;

        await loadFindings();
        await loadAIStatus();
    } catch (err) {
        status.textContent = err.message;
        status.className = 'scan-status err';
    } finally {
        btn.disabled = false;
        label.classList.remove('hidden');
        spinner.classList.add('hidden');
    }
}

// ── Findings ──────────────────────────────────────────────────
async function loadFindings() {
    try {
        const res = await fetch(`${API}/findings`);
        const data = await res.json();
        const body = document.getElementById('findings-body');

        if (!data.findings.length) {
            body.innerHTML = '<div class="empty-state">Run a scan to surface unprotected routes.</div>';
            document.getElementById('stat-findings').textContent = '0';
            return;
        }

        document.getElementById('stat-findings').textContent = data.total;

        body.innerHTML = data.findings.map((f, i) => `
            <div class="finding-row" style="animation-delay:${i * 30}ms"
                 onclick="viewPatch('${f._event_file}', '${f.function}')">
                <div class="finding-left">
                    <span class="severity-pip"></span>
                    <div class="finding-info">
                        <div class="finding-name">${f.function}</div>
                        <div class="finding-meta">${f.file}:${f.line}</div>
                    </div>
                </div>
                <div class="finding-right">
                    <div class="finding-time">${new Date(f.timestamp).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</div>
                    <div class="finding-action">View patch</div>
                </div>
            </div>
        `).join('');
    } catch {
        document.getElementById('findings-body').innerHTML =
            '<div class="empty-state" style="color:var(--red)">Failed to load findings</div>';
    }
}

// ── Patch viewer ──────────────────────────────────────────────
async function viewPatch(filename, funcName) {
    try {
        const res = await fetch(`${API}/findings/${filename}`);
        const data = await res.json();
        document.getElementById('patch-title').textContent = funcName;
        document.getElementById('patch-content').textContent = data.patch || 'No patch generated';
        document.getElementById('patch-modal').classList.remove('hidden');
    } catch {
        /* silently fail */
    }
}

function closePatch(event) {
    if (event && event.target !== event.currentTarget) return;
    document.getElementById('patch-modal').classList.add('hidden');
}

// ── Keys ──────────────────────────────────────────────────────
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePatch();
    if (e.key === 'Enter' && e.target.id === 'scan-target') runScan();
});

// ── Init ──────────────────────────────────────────────────────
checkHealth();
loadAIStatus();
loadFindings();
setInterval(checkHealth, 30000);
