# Procurement sandbox — contract

**Procurement sandbox — not SAP connected.** This service imitates the shape of three SAP S/4HANA Cloud OData v2 APIs so that Demand Pulse can be wired to a persistent procurement object with realistic request, response, error, concurrency and authorisation behaviour. It is not SAP software, holds no SAP data, and proves only the application-layer loop. Every response carries the header `X-Procurement-Sandbox: not-SAP-connected`.

Base URL (default): `http://127.0.0.1:8081`. Service root pattern follows SAP: `/sap/opu/odata/sap/<SERVICE>/`.

## 1. What is faithful to SAP and what is simplified

| Aspect | Faithful | Simplified or invented |
|---|---|---|
| Service names, entity set names, key field names | `API_PURCHASEORDER_PROCESS_SRV`, `API_MATERIAL_STOCK_SRV`, `API_PURCHASEREQ_PROCESS_SRV`; `A_PurchaseOrder`, `A_PurchaseOrderItem`, `A_PurchaseOrderScheduleLine`, `A_MatlStkInAcctMod`, `A_PurchaseRequisitionHeader`, `A_PurchaseRequisitionItem` | Only the fields listed in section 3 exist |
| OData v2 JSON envelope | `{"d": {...}}`, `{"d": {"results": [...]}}`, `__metadata.uri/type/etag`, `__deferred` for unexpanded navigation | No `$batch`, no `$links`, no `$count` |
| Dates and numbers | `Edm.DateTime` as `/Date(ms)/`, `Edm.DateTimeOffset` as `/Date(ms+0000)/`, `Edm.Decimal` as strings with 3 decimals, `Edm.Boolean` as JSON booleans | Input dates may also be ISO 8601 or `YYYY-MM-DD`; output is always SAP form |
| CSRF | `GET` with `X-CSRF-Token: Fetch` returns a token; every modifying request must send it or receives `403` with `x-csrf-token: Required` and body `CSRF token validation failed` | Token has no expiry |
| Error envelope | `{"error": {"code", "message": {"lang","value"}, "innererror": {"transactionid","timestamp","errordetails": [...]}}}` | Codes are sandbox codes prefixed `SB/`, except a few SAP-style message classes used for recognisability |
| Concurrency | `ETag` header and `__metadata.etag` on PO and PR; `If-Match` on `PATCH`/`DELETE`; `412 Precondition Failed` | PR creation checks the referenced PO's change timestamp through a custom field (section 5) |
| Query options | `$filter` with `Field eq 'value'` joined by `and`; `$expand`; `$top`; `$skip`; `$select`; `$format=json` | No functions, no `or`, no `substringof` |
| Authorisation | Modifying calls require a role; wrong role gives `403` | Role comes from header `X-Sandbox-Role` instead of a SAP user |
| Custom fields | Prefixed `YY1_` with S/4 suffix `_PRI` (purchase requisition item), the standard S/4HANA custom-field convention | These specific fields are ours |
| Release | Function imports `ReleasePurchaseRequisition` and `RejectPurchaseRequisition` | Modelled on SAP release-strategy behaviour; the real PR API's release interface was not verified |
| Idempotency and duplicate guard | — | `Idempotency-Key` header and the case/evidence duplicate check are sandbox extensions, documented in section 6 |
| Fault injection | — | `X-Sandbox-Fault` header, section 8 |

## 2. Authentication and roles

No SAP user. Each modifying call sends:

| Header | Values | Enforced on |
|---|---|---|
| `X-CSRF-Token` | token from a prior `GET` with `X-CSRF-Token: Fetch` | all `POST`, `PATCH`, `DELETE` |
| `X-Sandbox-Role` | `planner`, `procurement_approver`, `supplier`, `system` | create PR: `planner` or `system`; release/reject: `procurement_approver` only; `supplier` can never modify anything |

A `supplier` role on any modifying call returns `403 SB/AUTH_ROLE`. This is the sandbox's way of guaranteeing the plan's rule that a supplier's disclosure can never trigger a procurement submission.

## 3. Entities and fields

### `API_PURCHASEORDER_PROCESS_SRV` (read only)

`A_PurchaseOrder('4500001042')` with `$expand=to_PurchaseOrderItem/to_ScheduleLine`

| Field | Type | Seed value |
|---|---|---|
| `PurchaseOrder` | String(10) | `4500001042` |
| `PurchaseOrderType` | String(4) | `NB` |
| `Supplier` | String(10) | `0000100421` (NorthOrchard, synthetic) |
| `CompanyCode` / `PurchasingOrganization` / `PurchasingGroup` | String | `CA01` / `CA01` / `C01` |
| `DocumentCurrency` | String(5) | `CAD` |
| `CreationDate` | DateTime | 2026-10-20 |
| `LastChangeDateTime` | DateTimeOffset | seed timestamp; changes whenever the PO is updated; also the ETag |
| `PurchasingDocumentDeletionCode` | String(1) | `` |

Item `A_PurchaseOrderItem(PurchaseOrder='4500001042',PurchaseOrderItem='00010')`

| Field | Seed value |
|---|---|
| `Material` | `OJ-250` |
| `PurchaseOrderItemText` | `Orange juice 250 ml, 24 bottles per case` |
| `Plant` / `StorageLocation` | `CA10` (Toronto DC) / `DC01` |
| `OrderQuantity` / `PurchaseOrderQuantityUnit` | `120.000` / `CS` |
| `NetPriceAmount` / `NetPriceQuantity` / `DocumentCurrency` | `22.500` / `1.000` / `CAD` |
| `MaterialGroup` | `BEV-JUICE` |
| `PurchasingDocumentDeletionCode` | `` |

Schedule line `A_PurchaseOrderScheduleLine`: `ScheduleLine=0001`, `ScheduleLineDeliveryDate=2026-10-27`, `ScheduleLineOrderQuantity=120.000`, `DelivDateCategory=1`.

### `API_MATERIAL_STOCK_SRV` (read only)

`A_MatlStkInAcctMod?$filter=Material eq 'OJ-250' and Plant eq 'CA10'`

| Field | Seed value |
|---|---|
| `Material` / `Plant` / `StorageLocation` | `OJ-250` / `CA10` / `DC01` |
| `Batch` | `CIT-91` |
| `InventoryStockType` | `01` (unrestricted) |
| `MatlWrhsStkQtyInMatlBaseUnit` / `MaterialBaseUnit` | `240.000` / `CS` |

### `API_PURCHASEREQ_PROCESS_SRV` (read and write)

Header `A_PurchaseRequisitionHeader`

| Field | Type | Set by |
|---|---|---|
| `PurchaseRequisition` | String(10) | sandbox, sequence from `1000000001` |
| `PurchaseRequisitionType` | String(4) | client, `NB` |
| `PurReqnDescription` | String(40) | client |
| `SourceDetermination` | Boolean | client, default `false` |
| `CreatedByUser` | String(12) | sandbox, from role |
| `CreationDate` | DateTime | sandbox |
| `LastChangeDateTime` | DateTimeOffset | sandbox; also the ETag |
| `ProcessingStatus` | String(1) | sandbox: `N` not edited |
| `ReleaseStatus` **(simplified)** | String(1) | sandbox: `` awaiting release, `R` released, `X` rejected |
| `ReleasedByUser`, `ReleaseDateTime`, `RejectionReason` **(simplified)** | | sandbox |

Item `A_PurchaseRequisitionItem`

| Field | Required on create | Validation |
|---|---|---|
| `PurchaseRequisitionItem` | no | sandbox assigns `00010`, `00020`, ... |
| `PurchaseRequisitionItemText` | no | max 40 |
| `Material` | yes | must exist in seed materials, else `400 ME/006` |
| `Plant` | yes | must exist, else `400 ME/008` |
| `StorageLocation` | no | |
| `RequestedQuantity` | yes | decimal > 0 |
| `BaseUnit` | yes | must equal the material's base unit (`CS`), else `400 SB/UNIT` |
| `DeliveryDate` | yes | not before sandbox "now", else `400 ME/039` |
| `PurchaseRequisitionPrice`, `PurReqnPriceQuantity`, `PurReqnItemCurrency` | no | currency must be `CAD` if given |
| `PurchasingGroup`, `PurchasingOrganization` | no | default `C01` / `CA01` |
| `Supplier` (fixed supplier) | no | must exist if given |
| `RequisitionerName` | no | |
| `IsDeleted` | no | sandbox |
| `YY1_DemandPulseCase_PRI` | yes | case id, e.g. `CASE-1042` |
| `YY1_EvidenceVersion_PRI` | yes | hash or version id of the accepted evidence artifact |
| `YY1_Disposition_PRI` | yes | `CHANGE` only; keep/stop dispositions are not procurement objects |
| `YY1_Reason_PRI` | yes | max 255; the cited reason the approver reads |
| `YY1_RefPurchaseOrder_PRI` | yes | existing PO, else `400 SB/REF_PO` |
| `YY1_RefPurchaseOrderItem_PRI` | yes | existing item |
| `YY1_RefPOChangeDateTime_PRI` | yes | must equal the PO's current `LastChangeDateTime`, else `412 SB/STALE_BASELINE` (section 5) |
| `YY1_OpenUnknowns_PRI` | no | free text, max 255; the unknowns the approver must see |

## 4. Operations

| Operation | Method and path | Success | Errors |
|---|---|---|---|
| Fetch CSRF | `GET /sap/opu/odata/sap/API_PURCHASEREQ_PROCESS_SRV/` with `X-CSRF-Token: Fetch` | `200`, header `x-csrf-token` | |
| Read PO | `GET .../API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrder('4500001042')?$expand=to_PurchaseOrderItem/to_ScheduleLine` | `200`, `ETag` | `404 SB/NOT_FOUND` |
| Read stock | `GET .../API_MATERIAL_STOCK_SRV/A_MatlStkInAcctMod?$filter=...` | `200` | |
| Create PR (deep insert) | `POST .../API_PURCHASEREQ_PROCESS_SRV/A_PurchaseRequisitionHeader` body `{"PurchaseRequisitionType":"NB","PurReqnDescription":"...","to_PurchaseRequisitionItem":{"results":[{...}]}}` | `201`, `Location`, `ETag`, body is the created header with items | `400` validation, `403` CSRF or role, `409 SB/DUPLICATE_REQUEST`, `412 SB/STALE_BASELINE`, `422 SB/IDEMPOTENCY_KEY_REUSED` |
| Read PR | `GET .../A_PurchaseRequisitionHeader('1000000001')?$expand=to_PurchaseRequisitionItem` | `200` | `404` |
| List PRs | `GET .../A_PurchaseRequisitionHeader?$filter=ReleaseStatus eq ''` | `200` | |
| Release | `POST .../ReleasePurchaseRequisition?PurchaseRequisition='1000000001'&ReleaseCode='01'` | `200`, body header with `ReleaseStatus=R` | `403` role, `404`, `409 SB/ALREADY_DECIDED` |
| Reject | `POST .../RejectPurchaseRequisition?PurchaseRequisition='1000000001'&Reason='...'` | `200`, `ReleaseStatus=X` | same |
| Simulate PO change | `PATCH .../API_PURCHASEORDER_PROCESS_SRV/A_PurchaseOrderItem(PurchaseOrder='4500001042',PurchaseOrderItem='00010')` with `If-Match` and a body such as `{"OrderQuantity":"150.000"}` | `204`, new `ETag` | `412` on `If-Match` mismatch, `428` if missing |
| Audit | `GET /sandbox/audit` | list of every modifying call with request, response and role | |
| Reset | `POST /sandbox/reset` (role `system`) | re-seeds | |
| Health | `GET /sandbox/health` | `{"status":"ok","sap_connected":false}` | |

The `PATCH` on the PO exists only so the team can test the staleness rule: change the PO, then try to submit a PR prepared against the old baseline.

## 5. Staleness rule

A PR is prepared from a review that read the PO at some moment. The item carries `YY1_RefPOChangeDateTime_PRI` equal to the `LastChangeDateTime` the review saw. On create, the sandbox compares it with the PO's current value. If they differ, the create fails with `412 Precondition Failed`, code `SB/STALE_BASELINE`, and `errordetails` naming the current value. The application must show "re-approval needed", not "submitted".

## 6. Idempotency and duplicate guard

Two independent protections, both sandbox extensions:

1. **`Idempotency-Key` header.** Same key and byte-identical payload: `200` (not `201`) with the original object and header `Idempotent-Replayed: true`. Same key and a different payload: `422 SB/IDEMPOTENCY_KEY_REUSED`. Keys are kept for the life of the database.
2. **Case and evidence duplicate guard.** If a PR exists for the same `YY1_DemandPulseCase_PRI` and `YY1_EvidenceVersion_PRI` whose `ReleaseStatus` is not `X`, a second create returns `409 SB/DUPLICATE_REQUEST` with the existing `PurchaseRequisition` in `errordetails[0].target`. A new evidence version is a new request.

A retry therefore never creates a second object; a re-review with new evidence does.

## 7. Receipt states the application must distinguish

| Sandbox response | Application state to show |
|---|---|
| `201` on create | Submitted, awaiting procurement approval; show the PR number |
| `200` with `Idempotent-Replayed` | Already submitted; show the same PR number |
| `409 SB/DUPLICATE_REQUEST` | Already submitted for this evidence version; link to it |
| `412 SB/STALE_BASELINE` | Baseline changed since review; re-review and re-approval required |
| `400` validation | Rejected before submission; show the field findings |
| `403` | Not permitted for this role; never retry automatically |
| `5xx`, timeout | Submission failed; outcome unknown; retry with the same `Idempotency-Key` |
| Release `200` with `ReleaseStatus=R` | Approved by procurement; exception may close with the link |
| Reject `200` with `ReleaseStatus=X` | Returned by procurement; show the reason |

"Request sent" is never the same as "change completed".

## 8. Fault injection

Header `X-Sandbox-Fault` on any modifying call:

| Value | Behaviour |
|---|---|
| `http500` | `500` with the SAP error envelope, nothing persisted |
| `timeout` | sleeps `PROC_SANDBOX_TIMEOUT_SECONDS` (default 8) then `504`, nothing persisted |
| `locked` | `409 ME/006`-style "document locked by user ADMIN", nothing persisted |
| `accept_then_fail` | persists the object, then returns `502`: the client's retry with the same `Idempotency-Key` receives `200 Idempotent-Replayed`. This is the case that distinguishes "sent" from "completed" |

## 9. Mapping a Demand Pulse change draft to a PR

| Change draft field | PR field |
|---|---|
| case id | `YY1_DemandPulseCase_PRI` |
| accepted evidence artifact hash or id | `YY1_EvidenceVersion_PRI` |
| disposition (`CHANGE`) | `YY1_Disposition_PRI` |
| cited reason | `YY1_Reason_PRI` |
| open unknowns | `YY1_OpenUnknowns_PRI` |
| baseline PO, item, change timestamp seen | `YY1_RefPurchaseOrder_PRI`, `YY1_RefPurchaseOrderItem_PRI`, `YY1_RefPOChangeDateTime_PRI` |
| proposed additional quantity, unit | `RequestedQuantity`, `BaseUnit` |
| material, plant | `Material`, `Plant` |
| needed-by date | `DeliveryDate` |
| quoted price per case, currency | `PurchaseRequisitionPrice`, `PurReqnPriceQuantity=1`, `PurReqnItemCurrency` |
| supplier of the quote | `Supplier` |
| one-line description for the approver list | `PurReqnDescription` (40 chars) |
| original value versus proposed value | appears in `YY1_Reason_PRI`; the PO itself is read live for the original |

Keep-plan and stop dispositions create **no** procurement object. They are closed in the application with the reason, and the sandbox is not called.
