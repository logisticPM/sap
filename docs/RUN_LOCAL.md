# Local demo and deployment

## Public replay

GitHub Pages serves `web/`. It needs no backend, key or model account. All fixtures are public synthetic records with selected archived model/tool outputs. Browser localStorage holds sessions; open role links in the same browser to share progress. Use a new replay for a new branch. Clearing site storage removes those local sessions.

To serve it locally from the repository root:

```powershell
python -m http.server 8000 --directory web
```

Open `http://127.0.0.1:8000/`. GitHub Pages deploys from `.github/workflows/pages.yml`. No secret is needed in GitHub Actions.

## Local real-model backend

Requires Python 3.11+ and internet access to OpenRouter. This is a loopback demo, not an authenticated multi-user service.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r demo/requirements.txt
.\.venv\Scripts\python demo/server.py
```

Open `http://127.0.0.1:8796/`. Replay works without credentials. Real calls are disabled by default. Port 8796 keeps the original developer demo separate.

For **new real calls**, put your own key in `demo/.env` using the single-line pattern in `.env.example`, or set `OPENROUTER_API_KEY` in your local environment. Never commit it. Then, in the server terminal, explicitly set:

```powershell
$env:ENABLE_LIVE_MODEL = '1'
$env:DEMO_BUDGET_USD = '1'
.\.venv\Scripts\python demo/server.py
```

The example authorizes a separate $1 local reservation cap; choose 0–9 USD. It does **not** consume or reset the original project's $10 authorization. UI references to $10/$9 describe maximum ceilings; the configured cap may be lower. `demo/runtime/budget.sqlite` persists accounting across sessions. Never delete/reset it to evade a cap. Add a provider-side spending limit as well; the local estimate is not a billing guarantee. Uncertain/failed calls retain their reservation and do not automatically retry. Model/provider availability and actual charges may vary.

The model is `anthropic/claude-sonnet-4.6`. Live review, new reply and alternative investigation may each trigger calls. Sharing and closure are local human/rule actions. Real calls process only the frozen synthetic material; no production inbox or SAP system is accessed. Do not put real supplier material into this public demonstration package.

## Tests without model charges

```powershell
cd demo
python -m unittest test_workbench test_portable -v
```

Use a clean environment with live execution disabled for tests. The portable extraction has local tests; no additional paid call is claimed for this handoff release. Selected historical outputs originate in the previously tested v31.
