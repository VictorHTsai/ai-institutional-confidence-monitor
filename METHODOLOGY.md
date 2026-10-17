# AI Institutional Confidence Monitor — validation protocol v0.1

Status: RESEARCH GATE OPEN; NOT APPROVED FOR PRODUCTION. No conclusion about current institutional AI confidence is authorized by this document.

## Question and estimand

Measure changes in reported long-equity positions in a defined US Form 13F reporting population. Institutional confidence is an interpretation, never an observed variable. Neither purchases nor investor cash flows are identified from two portfolio snapshots. Issuance, stock compensation, conversions, acquisitions, in-kind transfers, manager reorganizations and filing coverage can change positions without open-market buying.

Primary candidate: a balanced panel of reporting managers with usable filings in every target quarter, 2021-12-31 through the most recent sufficiently covered period. This trades representativeness for comparability; it excludes new and disappearing managers and has survivorship bias. Publish full reporting-population counts and an adjacent-quarter matched-panel sensitivity beside it. Never silently treat an absent manager's filing as a zero position. A security absent from a manager's otherwise complete filing can be an observed reported zero, subject to de minimis omissions and confidentiality.

## Data chronology and provenance

SEC bulk ZIP windows are **filing windows**, not holdings periods. Read SUBMISSION.PERIODOFREPORT and reconcile COVERPAGE.REPORTCALENDARORQUARTER. The baseline normally arrives in 2022 filings, not the archive named 2021 Q4. Ingest every available filing window beginning 2021 Q4, retain accession-level source references, archive URLs, SHA-256 and retrieval timestamps. Historical series are restated using all available amendments as of retrieval; they are not point-in-time backtest inputs. Store filing dates to support an explicit as-of reconstruction later.

On 2026-10-17 the official bulk publication page lists June–August 2026 as its latest window. 2026 Q2 is a candidate latest mature observation, not yet a verified output. Early Q3 filings must not be compared with a mature Q2 population. Late amendments after August require an incremental EDGAR ingest, or a plainly stated bulk-data cut-off. Checking the archive page daily alone does not satisfy a daily new-filing requirement.

## Filing resolution and overlap

1. Unique accession + information-row key removes repeated archive ingestion, not economic overlap.
2. Group by manager CIK and report period. Read amendment type: a restatement replaces the applicable table; an amendment adding holdings appends to the applicable prior state. Selecting just the latest accession loses positions. Ambiguous chains, conflicting duplicates or a notice replacing a holdings report require quarantine and a reason.
3. Keep only SH equity rows, empty PUTCALL, verified security CUSIP/class. Convertible bonds, principal amounts, options and warrants are excluded. Do not discard legitimate multiple rows in one filing just because they share a CUSIP.
4. Resolve OTHERMANAGER and OTHERMANAGER2 through CIK and 13F file number. Manager relationships are a graph, not a string-name deduplication. Check shared-discretion rows and parent/subsidiary filers before summing. A group's representative filing cannot be chosen by size without checking whether its reporting scope contains its subsidiaries' positions.
5. If economic deduplication fails, publish the narrower **standalone-reporting-manager panel**: exclude unresolved linked managers and shared-discretion positions; report excluded managers/positions and residual duplication risk. This remains a panel of reported positions, not global institutional ownership.
6. Confidential holdings, de minimis omissions, incorrect filer submissions and undisclosed relationships cannot be fully repaired from bulk data. Coverage measures describe observed data, not proof of completeness.

## Corporate actions and security history

CUSIP mapping is dated and class-specific; ticker strings are insufficient. Verify the official 13F list and issuer filings. Normalize pre-split shares into one common unit and divide reference prices by the same factor. Validate NVDA 10:1 (2024), GOOG/GOOGL and AMZN 20:1 (2022), AVGO 10:1 (2024), NOW 5:1 (December 2025), plus any later actions through the actual observation date. The 2021 NVDA 4:1 split predates the baseline and must not be applied again to baseline shares. META's ticker/name change is not new accumulation. Corporate issuances and merger consideration remain distinct from open-market buying even after splits are adjusted.

TSM means US-reportable ADS/ADR CUSIP 874039100; never Taiwan ordinary shares or global TSMC institutional ownership. ASML's US-reportable registry shares likewise do not represent its complete worldwide shareholder base. GOOG and GOOGL stay separate in the security layer and combine once for issuer analysis.

CRWV begins after its IPO with its first mature quarter; never assign a pre-IPO zero and call its initial holdings net buying. NBIS must not inherit Yandex's 2021 economic baseline following the 2024 divestment. IREN/APLD's legacy mining/business exposures are not historical AI conviction. These satellites use separate inception/transition histories and are excluded from the fixed 2021 basket.

## Indicators and identities

For split-adjusted shares Q[i,t], verified quarter reference price P[i,t], fixed baseline price P[i,0]:

* Constant-price position stock B[t] = sum_i Q[i,t] P[i,0]. Primary level index I[t] = 100 B[t]/B[0], only for an unchanged security basket and unchanged manager panel with valid positive baseline prices. This is a quantity-position index with 2021 valuation weights; report concentration and equal-issuer-weight sensitivity.
* Estimated quarter-end-price net position change E[t] = sum_i (Q[i,t]-Q[i,t-1]) P[i,t]. This is an estimate of the dollar value of changes in reported positions, **not dollars actually spent**.
* Exact endpoint decomposition under this price convention: ΔV[t] = E[t] + sum_i Q[i,t-1](P[i,t]-P[i,t-1]). Reconcile to rounding tolerance; both terms use the same split-adjusted share unit. Display the convention, not just a dollar number.
* Accumulation A[t] = B[t]-B[0], peak H[t] = max(0,max_{s<=t} A[s]). Remaining accumulation R[t]=100 A[t]/H[t] only if H[t] is materially positive versus measurement uncertainty and data revisions. R may be negative if positions fall below baseline; never silently clamp to zero. If H is small or unstable, display N/A and show change versus baseline instead.
* Position-stock drawdown = 100(B[t]/max_{s<=t} B[s]-1). This differs from the percentage of post-baseline accumulation surrendered. Publish distinct labels.
* Satellite IPO/transition cohorts are not spliced into the fixed-basket level. Compare percentage position changes on a matched-manager basis after an eligible first-quarter baseline, with explicit differing history and denominator.

Reference prices should be verified market quarter-end closes from an auditable provider. SEC values/shares can supply an **as-filed implied price diagnostic**, not an automatically trusted close. Filing values historically used thousands of dollars; filings on/after 2023-01-03 changed to dollars. Determine schema/version and validate ratios across filers; do not guess that every row or every late amendment is correct. Never silently rescale suspicious rows. Until price and split reconciliation passes, withhold dollar changes and the aggregate weighted index; publish audited share changes only if independently valid.

## Rotation and attribution

Compute group changes using the same manager panel, dated eligibility, prices and controls. Show dollar position change and normalized change relative to each group's preceding stock. Opposite signs are consistent with rotation, not proof that the same money moved between groups. Matched-manager co-occurrence and portfolio-weight changes provide additional evidence, still without tracing transactions. Include non-AI benchmarks/total manager portfolio exposure before claiming AI-specific allocation rather than broad equity expansion. Benchmark data are outside the candidate-only staging extract and must be added before that claim.

13F cannot separate all active and passive sleeves within large mixed managers. Label classification unknown/mixed unless independently verified, and show any audited active-only subset separately. Do not equate a manager's net long stock additions with active conviction.

## Financing and thesis test

Do not assume all infrastructure firms are highly leveraged or all hyperscalers have positive current FCF. Assess issuer-quarter cash, total debt, leases, operating cash flow, capex, FCF definition, financing commitments, maturity walls and equity dilution separately. Compare common dated financial metrics. A financing rate in an issuer contract is not a traded credit spread. A broad high-yield spread is a macro control, not AI-company credit.

Predefine thesis evidence: falling infrastructure panel positions alongside resilient established-cloud/compute positions; independently observed financing deterioration; robustness across manager and price conventions. Holdings patterns alone cannot establish financing causation. Quarterly Q2 snapshots cannot verify September–October selling or hedge-fund historically elevated current net exposure. J.P. Morgan's original report has not been retrieved; its thesis here is the user-provided hypothesis, not a source independently authenticated by this project.

## Required validation before production

Reject publication when any required baseline/latest quarter is absent, an unresolved corporate action changes units, amendment scope is ambiguous for included managers, included linked-manager overlap is unresolved, a CUSIP is unverified, or price/valuation identities fail. Produce quarter-by-quarter filing counts, matched/balanced-manager counts, excluded relationship counts and position share, missing/zero distinctions, stale/partial-quarter status, quarantine reasons, price-diagnostic distributions and archive checksums. Flag suspicious positions exceeding independently verified eligible shares outstanding; this requires correct ADR units and class float/issued-share definitions.

Meaningful tests: split invariance, appreciation-only zero position change, restatement versus additive amendment, repeated-archive idempotence, shared-manager exclusion, IPO exclusion from baseline, missing filing versus reported zero, dollar-unit transition, negative/near-zero accumulation denominator, decomposition identity, partial latest-quarter refusal and source-to-output row audit.

## Short gate assessment

Reliable after validation: a specified reporting panel's quarterly reported long-share positions, corporate-action-adjusted changes, filing coverage and observed group patterns.

Estimated after price validation: standardized dollar position changes and constant-price position indices. These do not identify transaction prices or money contributed.

Not identifiable from 13F alone: exact flows, global ownership, shorts/hedge-fund net exposure, daily positioning, investor intent, AI-only earnings exposure, or causal transfers between groups.

Current decision: ingestion is under way. The final methodology gate has **not passed**. Do not deploy a numeric research dashboard or describe the project as complete until the actual tests and coverage report exist.

## Primary references

* SEC bulk data: https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets
* SEC table specification: https://www.sec.gov/files/form_13f.pdf (historical document; its value-unit description must be checked against later amendments)
* SEC FAQ, especially amendments/shared discretion and Q62: https://www.sec.gov/rules-regulations/staff-guidance/frequently-asked-questions-about-form-13f
* NVIDIA split 8-K: https://www.sec.gov/Archives/edgar/data/1045810/000104581024000144/nvda-20240607.htm
* Broadcom split 8-K: https://www.sec.gov/Archives/edgar/data/1730168/000114036124033072/ny20032136x6_8k.htm
* NOW 2025 10-K: https://www.sec.gov/Archives/edgar/data/1373715/000137371526000007/now-20251231.htm
* Nebius divestment: https://nebius.com/newsroom/ynv-announces-successful-completion-of-the-divestment-of-its-russia-based-businesses

## Restricted release amendment (2026-10-17)

The original full-population gate above remains open. See RELEASE_ASSESSMENT.md for the narrower released reporting-panel estimand, actual validation results and outstanding original acceptance criteria. The implemented restricted panel excludes amended manager histories instead of attempting unreviewed amendment-chain reconstruction. Its dollar estimates deliberately use internally consistent SEC implied prices and are labeled proxies; this relaxes the independent-market-price requirement only for this descriptive release, not for the original capital-confidence objective. Remaining accumulation is withheld. No representative/global/active-confidence interpretation is authorized.
