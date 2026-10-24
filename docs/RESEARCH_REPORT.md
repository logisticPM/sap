# Research report — evidence and limits

This is a synthesis of existing project records and previously reviewed public sources, not a new field study. Public references below support bounded propositions; they are not evidence of our product's measured benefit. Source review date in project records: 23–24 October 2026.

## 1. Why investigate the workflow?

The [GCA/YouGov 2025 qualitative study](https://assets.publishing.service.gov.uk/media/68dd577ec487360cc70ca001/YouGov_slides_-_GCA_Annual_conference_2025.pdf) describes supplier experiences with retailer forecasting and ordering. It interviewed 28 suppliers; this is qualitative UK evidence, not a Canadian prevalence estimate. The [ACCC supplier roundtable summary](https://www.accc.gov.au/system/files/supermarkets-inquiry-summary-roundtables.pdf) records participant concerns around forecasting, orders and supply relationships. Those are participant views, not causal findings about software or Canadian operations.

Closer to the target setting, [Loblaw's PO Updates user guide](https://scvendorportal.loblaw.ca/LCLSCVendorPortal_POUpdatesUserGuide.pdf) describes a structured purchase-order update workflow. [Mucci Farms careers materials](https://www.muccifarms.com/careers/) describe responsibilities involving schedules, customer requirements, warehouse/QA coordination and documentation. These support multi-party coordination as a plausible task. They do **not** establish that suppliers only use Excel, measure their delay, or prove that a new portal will be adopted. Job postings and online guides may change; the cited review is a dated desk study.

Our pre-order additional-supply inquiry is adjacent to those published workflows. CASE-1042, its cutoff, quantities, brands and replies are authored test materials, not a Loblaw/Mucci transaction.

## 2. Internal experiments constrain the product claims

All monetary-looking values below are normalized simulated price units, not dollars. Demand reconstruction and cost assumptions restrict external validity.

| Experiment / original record | Finding | Consequence |
|---|---|---|
| [E1 strict online boundary](../evidence/E1_REPORT.txt) | P5 trailed P2 by 20.86046 normalized units in the frozen test | Do not advertise the complete strategy as superior |
| [E2 four-way ablation](../evidence/ABLATION_REPORT.txt) | P2 + transfer gained only 0.79014 normalized units; detection/response components could hurt | Separate modules; tiny simulated gains are insufficient |
| [E3 fresh-network replication](../evidence/REPLICATION_REPORT.txt) | Failed preregistered replication criterion; aggregate +0.91990757 but two cities negative and fulfillment declined | No reliable transfer advantage; no complete-cost ROI claim |
| [E4 artificial censor recovery](../evidence/RECOVERY_REPORT.txt) | P2 lowered absolute recovery error but underestimated hidden sales by 23.193% versus 4.2417% for the baseline | Better error metric is not unbiased latent-demand recovery or better ordering |

E3 used different policy-scored city networks within the same retailer/period, not a prospective trial. E4 masks known in-stock observations; it cannot observe true lost demand during real stockouts and has selection limits. Full experiments are not reproduced by this demo package; original summaries are supplied for audit, raw datasets are not redistributed.

## 3. Academic methods worth borrowing

**FreshRetailNet-50K:** [paper](https://arxiv.org/html/2505.16319v1), [dataset documentation](https://huggingface.co/datasets/Dingdong-Inc/FreshRetailNet-50K/blob/main/README.md). Separate censored-demand reconstruction from forecasting and evaluate on artificial masks with known targets. The paper's TFT WAPE comparison, 31.75% to 29.02%, is a 2.73 percentage-point predictive metric difference, not replenishment profit. Its setting and units cannot be mapped directly to our fictional Toronto juice case. Our current follow-up demo does not invoke an FRN forecast at runtime.

**Procurement task study:** [DOI 10.1016/j.procs.2026.02.467](https://doi.org/10.1016/j.procs.2026.02.467). The reviewed paper used five participants, six synthetic offers and nine tasks. Borrow task-level scoring and source-grounded comparison. Do not claim a validated human-plus-Agent efficiency effect: that group is absent, and the project review identified inconsistent reported timing statistics. The copyrighted PDF is not redistributed here.

**Tool-mediated supply-chain reasoning:** [arXiv 2507.21502](https://arxiv.org/pdf/2507.21502). Borrow the distinction between language-based orchestration and established numerical tools, preserving baseline/what-if comparisons. Enterprise estimates and reported case results do not establish causal retail benefits for this product.

## 4. Strongest counterarguments

- The binding delay may be production, transport or commercial commitment; faster document review would not change arrival.
- Structured fields and rules may already solve this narrow task more cheaply.
- The supplier may reject another portal or be unwilling to disclose information; collection effort could exceed the planner's savings.
- The Agent is given explicit expected condition states by the harness. This proves constrained execution, not autonomous supply-chain understanding.
- Missing forecast metadata prevents a justified additional quantity even after supply facts are clarified.

## 5. Evidence still missing

No direct target-user interviews, paired communications/order histories, actual active-work timing, supplier participation rate, implementation-cost quote, real SAP integration test or prospective fulfillment outcome exists in this package. Public evidence establishes plausibility of the problem class, not our effect size or competitive advantage. See [the validation plan](VALIDATION.md) for the next falsifiable test.
