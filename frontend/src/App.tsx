import { useMemo, useState } from 'react'
import './App.css'

const LANG_SNIPPETS = {
  curl: `curl https://api.concise.dev/v1/compress \\
  -H "X-API-Key: $CONCISE_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "def fibonacci(n): ...",
    "level": "balanced"
  }'`,
  node: `import fetch from 'node-fetch'

const payload = {
  text: systemPrompt,
  level: 'aggressive',
  use_cache: true
}

const res = await fetch('https://api.concise.dev/v1/compress', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': process.env.CONCISE_KEY ?? ''
  },
  body: JSON.stringify(payload)
})

const data = await res.json()`,
  python: `import os
import requests

payload = {
    "text": system_prompt,
    "level": "conservative",
    "use_cache": False,
}

resp = requests.post(
    "https://api.concise.dev/v1/compress",
    headers={"X-API-Key": os.environ["CONCISE_KEY"]},
    json=payload,
)
resp.raise_for_status()
print(resp.json()["compressed_text"])`
} as const

const DOC_CALLOUTS = [
  {
    title: 'FastAPI control plane',
    body: 'Includes auth, key management, OpenAI proxy, compression, usage, TALE optimization routes.',
    source: 'backend/app/main.py',
    action: 'Explore API surface'
  },
  {
    title: 'Compression service internals',
    body: 'LLMLingua2 + python-minifier combo with GPU offload and CPU fallback logic.',
    source: 'backend/app/services/compression.py',
    action: 'Read implementation'
  },
  {
    title: 'Playbooks & evidence',
    body: 'SUCCESS_SUMMARY.md and CURRENT_STATUS.md log every run with ratios, latency, cache hits.',
    source: 'SUCCESS_SUMMARY.md',
    action: 'Open research log'
  }
]

const ASCII_LOGO = `
           ██████████
        ███░░░░░░░░░░███
      ██░░░░░░░░░░░░░░░██
    ██░░░░░░░░░░░░░░░░░░██
   ██░░░░░░░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░░░░░░░██
 ██░░░░░░░░░░░░░░░░░░░░░░░░██
 ██░░░░░░░░░░░░░░░░░░░░░░░░██
██░░░░░░░░░░░░░░░░░░░░░░░░░░██
██░░░░░░░░░███░░░░░░░░░░░░░░██
██░░░░░░░███████░░░░░░░░░░░░██
██░░░░░░░░░███░░░░░░░░░░░░░░██
██░░░░░░░░░░░░░░░░░░░░░░░░░░██
 ██░░░░░░░░░░░░░░░░░░░░░░░██
  ██░░░░░░░░░░░░░░░░░░░░░██
   ███░░░░░░░░░░░░░░░░███
      █████░░░░░░█████
         ██████████
`

const HERO_STATS = [
  { label: 'Smoke test', value: '72 → 55 tokens', hint: 'balanced · CURRENT_STATUS.md' },
  { label: 'Latency window', value: '150–2000 ms', hint: 'LLMLingua CPU+GPU pathways' },
  { label: 'Cache hit rate', value: '82%', hint: 'proxy usage logs' }
]

const INTEGRATIONS = [
  {
    title: 'Proxy middleware',
    detail: 'Drop-in Express handler that compresses before relaying to OpenAI.',
    code: `app.post('/chat', async (req, res) => {
  const compressed = await concise.compress({
    text: req.body.prompt,
    level: 'balanced'
  })
  const response = await openai.chat({ prompt: compressed })
  res.json(response)
})`
  },
  {
    title: 'Edge worker',
    detail: 'Cloudflare worker hitting the hosted /v1/compress endpoint.',
    code: `export default {
  async fetch(request, env) {
    const payload = await request.json()
    const compressed = await env.CONCISE.fetch('/v1/compress', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    return new Response(compressed.body)
  }
}`
  }
]

function App() {
  const [lang, setLang] = useState<keyof typeof LANG_SNIPPETS>('curl')

  const asciiLines = useMemo(
    () => ASCII_LOGO.trim().split('\n'),
    []
  )

  return (
    <div className="page">
      <header className="nav">
        <div className="brand">
          <div className="brand__glyph">C</div>
          <div>
            <p>Concise</p>
            <span>Compression OS</span>
          </div>
        </div>
        <div className="nav__actions">
          <button className="ghost">Docs</button>
          <button className="ghost">Research log</button>
          <button>Launch console</button>
        </div>
      </header>

      <section className="hero">
        <div className="hero__text">
          <p className="kicker">LLMLINGUA · PYTHON-MINIFIER · TALE</p>
          <h1>Compress every token, keep every thought.</h1>
          <p>
            A FastAPI control plane that proxies OpenAI-compatible traffic,
            runs LLMLingua2 on long-form text, minifies Python with python-minifier,
            and feeds TALE output budgets back into your agents. Zero hallucinated summaries,
            just provable savings backed by CURRENT_STATUS.md.
          </p>
          <div className="hero__cta">
            <button>Get API access</button>
            <button className="secondary">Read docs</button>
            <button className="ghost">View SUCCESS_SUMMARY.md</button>
          </div>
          <div className="metrics">
            {HERO_STATS.map((item) => (
              <article key={item.label}>
                <p>{item.label}</p>
                <h3>{item.value}</h3>
                <span>{item.hint}</span>
              </article>
            ))}
          </div>
        </div>

        <div className="hero__visual">
          <pre aria-hidden className="ascii">
            {asciiLines.map((line) => (
              <span key={line}>{line}</span>
            ))}
          </pre>
          <div className="hero__callout">
            <p>Last run</p>
            <h4>token_compression_code</h4>
            <p>Fibonacci auth routine · 34 → 23 tokens · 12.79 ms</p>
            <span>backend/PRODUCTION_STATUS.md</span>
          </div>
        </div>
      </section>

      <section className="snippets">
        <div className="snippets__header">
          <div>
            <p className="kicker">Integration snippets</p>
            <h2>Docs-worthy code blocks shipped with the repo</h2>
          </div>
          <div className="lang-toggle">
            {(Object.keys(LANG_SNIPPETS) as (keyof typeof LANG_SNIPPETS)[]).map((key) => (
              <button
                key={key}
                className={key === lang ? 'active' : ''}
                type="button"
                onClick={() => setLang(key)}
              >
                {key}
              </button>
            ))}
          </div>
        </div>
        <div className="snippet-grid">
          <article className="code-card">
            <header>
              <span>/v1/compress</span>
              <span>docs/README.md</span>
            </header>
            <pre>
              <code>{LANG_SNIPPETS[lang]}</code>
            </pre>
          </article>
          {INTEGRATIONS.map((integration) => (
            <article key={integration.title} className="code-card">
              <header>
                <span>{integration.title}</span>
                <span>{integration.detail}</span>
              </header>
              <pre>
                <code>{integration.code}</code>
              </pre>
            </article>
          ))}
        </div>
      </section>

      <section className="docs">
        <p className="kicker">Source of truth</p>
        <h2>Every claim links back to this repo</h2>
        <div className="docs__grid">
          {DOC_CALLOUTS.map((callout) => (
            <article key={callout.title}>
              <h3>{callout.title}</h3>
              <p>{callout.body}</p>
              <footer>
                <span>{callout.source}</span>
                <button className="ghost">{callout.action}</button>
              </footer>
            </article>
          ))}
        </div>
      </section>
    </div>
  )
}

export default App
