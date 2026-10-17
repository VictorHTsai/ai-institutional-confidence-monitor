# Release assessment — 2026-10-17

## Gate decision

**PASS only for a narrower descriptive reporting-panel release. FAIL / incomplete for the original whole-institution capital-confidence objective.** The two decisions must not be conflated. The original proposed index cannot yet be published as a representative institutional-capital indicator. The dashboard therefore prominently labels all numerical series as a restricted reporting-manager panel and withholds an overall confidence score, remaining accumulation, active-only positioning and credit-spread series.

The restricted release describes reported positions; it does not establish the representativeness, economic completeness or active conviction of those positions. SEC provenance establishes where observations were filed, not that the filer made no mistakes.

## Actually processed

20 SEC bulk filing windows, from the 2021 Q4 filing archive through the June–August 2026 archive. 1,549,996 candidate information-table rows staged, including rows subsequently excluded. Actual report periods span a wider range because late amendments appear in later filing windows. Target history is 19 consecutive report quarters, 2021 Q4–2026 Q2. The publication cut-off is August 31, 2026; this is not October 17 holdings information.

6,253 managers had filings in all target periods before controls. The restricted balanced panel contains **1,188 CIKs**, compared with 10,793 observed reporting CIKs in Q2 2026: **11.0% by manager count**, explicitly not by assets or ownership market value. The list is included in data/panel.json. Panel construction excludes entire histories affected by amended/multiple/notice filings, manager relationships, shared discretion, confidential omission flags, missing or conflicting metadata, and suspicious implied-price ratios. Relationships are checked through both CIK and 13F file number. Residual undisclosed overlap remains possible; this is not an economically exhaustive deduplication of all 13F ownership.

The production numeric universe is 19 securities / 18 issuers: NVDA, AMD, AVGO, MRVL, TSM ADS, ASML US-reportable registry shares, MU, MSFT, GOOG, GOOGL, AMZN, META, PLTR, NOW, CRM, ORCL, CRWV, NBIS, APLD. The fixed 2021 core is 15 securities / 14 issuers. ORCL is a separate overlay. CRWV/NBIS/APLD are separate inception/transition cohorts. IREN remains a research candidate and financing-document reference, but is quarantined from numeric publication because early implied-price-reference counts are 7, 6 and 15, below the predeclared minimum of 20. No imputation is used.

## What passed

* Archive retrieval and CSV parsing, including a real SEC archive with nested directories; archive SHA-256 receipts retained.
* Idempotent re-run of the full archive inventory (all 20 recognized without duplicating staged observations).
* 19 consecutive target quarters for every fixed-core security; positive reported position stocks; finite baseline-normalized output.
* Corporate action normalization for NVDA, AMZN, GOOG/GOOGL, AVGO and NOW, including the December 2025 NOW split.
* Median implied-price reference: at least 20 eligible observations per published security-quarter; median absolute relative deviation <=1%. Core minimum reference counts range from 212 upward. This tests internal consistency, not independent exchange-price validation.
* Mathematical tests for appreciation versus position changes, split invariance, endpoint valuation decomposition, missing data, restatement versus additive amendments, small/negative accumulation denominators, manager-exclusion behavior, archive layouts and refusal to deploy pending data.
* Actual security-quarter endpoint decompositions are calculated and reconciled using the same adjusted units and SEC implied-price convention.

## What is estimated

Dollar position changes use the median of value/shares reported by eligible standalone filers, with pre-January-3-2023 filing values converted from thousands to dollars and split units aligned. The reference is an **as-filed implied price proxy**, not an independently verified exchange close or transaction price. Suspicious manager ratios are excluded, not silently rescaled. Constant-price indices use the corresponding baseline implied-price weights. The exact convention is recorded in code and the dashboard. These are estimates of the endpoint value of reported position changes, not cash flows or purchases.

## Findings limited to this sample

Q2 2026 versus Q1: fixed-core position index -1.63%; compute -4.87%; established platforms -0.36%; software -8.66%; ORCL overlay +3.10%; CRWV/NBIS/APLD group +71.08% in its own shorter history. The core index is 70.56 versus 2021 Q4=100. These are the restricted panel's quantities at fixed reference prices. They are **not** a finding that all institutions removed 29.44% of their AI capital. New issuance, changing client accounts and manager business structures can affect quantities without open-market purchases or sales. Baseline universe selection is retrospective.

These observations do not independently validate J.P. Morgan's October 17 thesis. In particular, June holdings cannot describe September–October selling. The original J.P. Morgan report has not been independently retrieved; the tested hypothesis is the user's description. No market-wide AI confidence verdict is released.

## Still outstanding against original acceptance criteria

* Full reporting-population economic deduplication and inclusion of amended filing chains rather than conservative exclusion.
* Source-wide information-table row-count reconciliation against filing summaries, independent share-count ceilings, benchmark/total-portfolio allocation controls and broader manager-sample sensitivity.
* Independent exchange prices; active/passive sleeve and hedge-fund classification; causal attribution to financing stress.
* Representative full-universe accumulated-capital / remaining-accumulation indicator. It remains withheld.
* Comparable issuer-quarter financing/FCF/leverage and actual credit-spread history. Primary documents are linked, no synthetic series is substituted.
* Individual newly published filings: recent SEC daily indexes are checked and arrivals are queued, but their positions are not incrementally merged. Verified numerical updates currently follow bulk releases.
* New reporting quarters require explicit corporate-action and eligibility review. The publication guard intentionally rejects an unsupported future-quarter change.
* Cloud execution and public hosting must be verified from actual GitHub Actions results; presence of a YAML file is not proof of execution.

## Update mechanics

Daily/manual workflow checks release discovery, stages archives and historical revisions, rebuilds the restricted panel, runs tests, commits updated public JSON and deploys Pages. Failures stop publication, retain the last published data and upload diagnostics to the failed run; GitHub notification settings determine email delivery. A local daily-index check observed 1,050 recent 13F arrivals but received HTTP 403 for the October 12 index. It correctly exited nonzero rather than claiming a successful complete check. This local result is not proof of the cloud runner's network behavior.

Refreshing an existing archived row with changed content is recorded as a conflict; conflicting corrections are not silently published. Metadata versions are preserved. The initial staging run predates accession-source receipt support for some older archives, so archive hashes and accession references are available but all per-archive accession links require a refreshed ingest. This is another reason the full original gate remains incomplete.
