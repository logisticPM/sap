# Procurement sandbox — not SAP connected

An S/4HANA-shaped mock of three OData v2 services (purchase order read, material stock read, purchase requisition read/write) so Demand Pulse can be wired to a **persistent procurement object** with realistic CSRF, role, ETag, idempotency, duplicate, staleness, error and failure behaviour. It is not SAP, holds no SAP data, and every response says so in the header `X-Procurement-Sandbox: not-SAP-connected`.

The full request/response contract, field list and the mapping from a Demand Pulse change draft to a purchase requisition are in [CONTRACT.md](CONTRACT.md). Read section 7 of that file first: it lists the application state each sandbox response must map to, and why "request sent" is never "change completed".

## Run

From this repository's root folder (`team_handoff_v31/`), with the project's existing virtual environment one level up (Starlette, uvicorn, pydantic, httpx and pytest are already installed; no new packages). Any Python 3.10+ with `starlette uvicorn httpx pytest` works too.

```bash
..\.venv\Scripts\python -m procurement_sandbox --port 8081
```

**Reaching it from the cloud workbench.** The deployed app on chatgpt.site cannot see a laptop's `127.0.0.1`. The zero-setup option is a Cloudflare quick tunnel, which needs no account and prints a public `https://*.trycloudflare.com` URL:

```bash
cloudflared tunnel --url http://127.0.0.1:8081
```

Point the app's procurement base URL at that address for the session. The URL changes on every start, so it is for development runs, not for a demo you cannot restart. For something stable, run the sandbox on any small Python host, or port `app.py` to a route inside the deployment; the contract is identical either way.

Options: `--host`, `--port`, `--db <sqlite path>` (default `procurement_sandbox/data/sandbox.sqlite`). Environment: `PROC_SANDBOX_DB`, `PROC_SANDBOX_PORT`, `PROC_SANDBOX_TIMEOUT_SECONDS` (delay for the `timeout` fault, default 8).

Health: `GET http://127.0.0.1:8081/sandbox/health` returns `"sap_connected": false`.

## Tests

```bash
..\.venv\Scripts\python -m pytest procurement_sandbox/tests -q
```

34 tests in three files. `test_contract.py` (21) covers the service itself; `test_client.py` (6) covers the reference client and its state mapping; `test_acceptance.py` (7) covers the freeze tool and the scorer. The contract tests cover: the label on every response; CSRF refusal in SAP form; supplier role can never modify; release and reject only by `procurement_approver`; PO and stock reads in OData v2 shape with ETags and deferred navigation; `$metadata`; deep-insert create; three input date formats; field-level validation with nothing persisted; keep/stop dispositions never create an object; idempotent replay and key reuse; duplicate case/evidence guard; staleness after a PO change; `If-Match` on PO patch; the four fault injections; audit; reset; persistence across restart.

## Reference client and acceptance kit

- [`client.py`](client.py): `ProcurementClient` with `read_purchase_order`, `read_stock`, `submit_change_draft`, `resolve_unknown`, `release`, `reject`, plus `map_change_draft` (CONTRACT §9) and the state names of CONTRACT §7. `python -m procurement_sandbox.client --base http://127.0.0.1:8081` runs the whole loop against a live sandbox and prints each state, including the 412 after a PO change.
- [`acceptance/`](acceptance/README.md): ten frozen engineering-acceptance tasks (`tasks.json`, hashed in `freeze.json`), the `case_export.json` contract the application must emit, and `score.py`, which cross-checks the application's claims against the sandbox's own records and writes a report that states no business value.

## Sixty-second walkthrough

```bash
# 1. token
curl -si http://127.0.0.1:8081/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV/ -H "X-CSRF-Token: Fetch" | grep -i x-csrf-token
```

```bash
# 2. read the baseline PO (note the ETag; the review must carry its timestamp)
curl -s "http://127.0.0.1:8081/sap/opu/odata/sap/API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('4500001042')?\$expand=to_PurchaseOrderItem/to_ScheduleLine"
```

```bash
# 3. submit a change request (replace TOKEN; the timestamp must equal the PO's current LastChangeDateTime)
curl -si -X POST http://127.0.0.1:8081/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV/A_PurchaseRequisitionHeader \
  -H "X-CSRF-Token: TOKEN" -H "X-Sandbox-Role: planner" -H "Idempotency-Key: case-1042-ev-a-v3" -H "Content-Type: application/json" \
  -d '{"PurchaseRequisitionType":"NB","PurReqnDescription":"CASE-1042 OJ-250 add 140 cases","to_PurchaseRequisitionItem":{"results":[{"Material":"OJ-250","Plant":"CA10","StorageLocation":"DC01","RequestedQuantity":"140","BaseUnit":"CS","DeliveryDate":"2026-10-28","PurchaseRequisitionPrice":"24","PurReqnPriceQuantity":"1","PurReqnItemCurrency":"CAD","Supplier":"0000100421","YY1_DemandPulseCase_PRI":"CASE-1042","YY1_EvidenceVersion_PRI":"ev-a-v3","YY1_Disposition_PRI":"CHANGE","YY1_Reason_PRI":"Authorised quote CIT-92; carrier accepted; 140 cases under 20% cancellation stress.","YY1_OpenUnknowns_PRI":"QA release reported, not independently verified","YY1_RefPurchaseOrder_PRI":"4500001042","YY1_RefPurchaseOrderItem_PRI":"00010","YY1_RefPOChangeDateTime_PRI":"2026-10-23T14:40:00Z"}]}}'
```

```bash
# 4. approve as procurement (replace TOKEN and the number)
curl -si -X POST "http://127.0.0.1:8081/sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV/ReleasePurchaseRequisition?PurchaseRequisition='1000000001'&ReleaseCode='01'" \
  -H "X-CSRF-Token: TOKEN" -H "X-Sandbox-Role: procurement_approver"
```

Repeat step 3 with the same `Idempotency-Key` to see `200 Idempotent-Replayed: true`. Change the PO first (`PATCH A_PurchaseOrderItem(...)` with `If-Match`) to see `412 SB/STALE_BASELINE`. Add `X-Sandbox-Fault: accept_then_fail` to see the one failure that only a retry resolves.

## Handoff to the application (Codex)

- The application calls the three services exactly as it would call SAP: fetch a CSRF token, read the PO and stock with their ETags before a review, carry `LastChangeDateTime` into the review artifact, and on planner authorisation `POST` the deep-insert with an `Idempotency-Key` derived from case id plus evidence version.
- Map responses to UI states with CONTRACT.md section 7. `201` is "awaiting procurement approval"; only a release `200` with `ReleaseStatus=R` closes the exception.
- Roles are plain headers here. The application must set `X-Sandbox-Role` from its own authorisation gate; the sandbox refuses `supplier` on every write so the "disclosure never submits" rule is enforced twice.
- **Hosting.** The cloud workbench on chatgpt.site cannot reach a laptop's `127.0.0.1`. Options, in order of least work: run the sandbox on a small public host (any Python host or a Cloudflare Tunnel in front of the laptop) and point the app at it; or port `app.py` to a Worker route inside the deployment. The contract is the same either way; this folder stays the reference implementation and test suite.
- The seed is the CASE-1042 baseline from the v47 synthetic pack: PO `4500001042` item `00010`, 120 cases inbound for 2026-10-27, 240 cases on hand at `CA10`/`DC01`, supplier `0000100421`. Reset with `POST /sandbox/reset` and role `system`.

## Fidelity, in one sentence

Service and entity names, OData v2 envelope and date encoding, CSRF handshake, error envelope, ETag concurrency and the `YY1_` custom-field convention follow S/4HANA; the role header, idempotency key, duplicate guard, fault injection and the release function imports are sandbox extensions, listed as such in CONTRACT.md section 1.
