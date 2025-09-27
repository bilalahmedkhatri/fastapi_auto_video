// filepath: /app/api/video-builder/scripts/route.js
// Generic proxy from Next.js (App Router) to FastAPI backend:
// Target FastAPI base: process.env.VIDEO_BUILDER_API_BASE (e.g. http://localhost:8000/api/video-builder/v1)
// Usage from client: fetch('/api/video-builder/scripts?child=jobs')
// Optional deeper path: /api/video-builder/scripts?child=jobs/run
// Pass through query params (except 'child') automatically.

const BASE = process.env.VIDEO_BUILDER_API_BASE || 'http://localhost:8000/api/video-builder/v1';

function buildTarget(req) {
    const url = new URL(req.url);
    const child = url.searchParams.get('child');
    if (!child) {
        throw new Error('Missing required query param "child" (e.g. ?child=jobs or ?child=jobs/run)');
    }

    // Reconstruct remaining search params excluding child
    const forwardParams = [];
    url.searchParams.forEach((v, k) => {
        if (k !== 'child') forwardParams.push(`${encodeURIComponent(k)}=${encodeURIComponent(v)}`);
    });

    const qs = forwardParams.length ? `?${forwardParams.join('&')}` : '';
    return `${BASE.replace(/\/$/, '')}/${child.replace(/^\/+/, '')}${qs}`;
}

async function proxy(req, method) {
    let target;
    try {
        target = buildTarget(req);
    } catch (e) {
        return new Response(JSON.stringify({ error: e.message }), { status: 400, headers: { 'Content-Type': 'application/json' } });
    }

    const headers = new Headers(req.headers);
    headers.delete('host');
    headers.delete('content-length');

    const init = {
        method,
        headers,
        redirect: 'manual',
    };

    if (method !== 'GET' && method !== 'HEAD') {
        // Stream/body clone
        init.body = await req.arrayBuffer();
    }

    let upstream;
    try {
        upstream = await fetch(target, init);
    } catch (err) {
        return new Response(JSON.stringify({ error: 'Upstream fetch failed', detail: String(err) }), {
            status: 502,
            headers: { 'Content-Type': 'application/json' },
        });
    }

    // Pass through body & status
    const respHeaders = new Headers(upstream.headers);
    // Optional: strip hop-by-hop headers
    ['transfer-encoding', 'connection'].forEach(h => respHeaders.delete(h));

    return new Response(upstream.body, { status: upstream.status, headers: respHeaders });
}

export async function GET(req) {
    return proxy(req, 'GET');
}

export async function POST(req) {
    return proxy(req, 'POST');
}

export async function PUT(req) {
    return proxy(req, 'PUT');
}

export async function PATCH(req) {
    return proxy(req, 'PATCH');
}

export async function DELETE(req) {
    return proxy(req, 'DELETE');
}

// (Optional) If you want a dynamic path instead of query (?child=...),
// create file: /app/api/video-builder/v1/[...slug]/route.js and map slug segments:
// const path = params.slug.join('/'); then target = `${BASE}/${path}`

export const config = {
    api: {
        bodyParser: false, // allow raw forwarding
    },
};