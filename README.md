# AI Institutional Confidence Monitor

A reproducible SEC Form 13F **restricted reporting-panel** dashboard. The original goal of measuring representative institutional AI capital confidence is **not yet complete**. Start with [RELEASE_ASSESSMENT.md](RELEASE_ASSESSMENT.md); it distinguishes the narrower release from outstanding acceptance criteria.

19 quarters (2021 Q4–2026 Q2), 20 source archives, 1,188 continuously reporting managers after conservative exclusions, 19 published securities / 18 issuers. Long-share quantities and fixed-price indices are distinct from price appreciation. Dollar position changes use disclosed SEC as-filed implied-price proxies, not actual purchases or cash flows. IREN and remaining-accumulation percentages are withheld under the documented gates.

## Reproduce with Python 3.12+

No third-party Python packages required:

```sh
python -m unittest discover -s tests -v
python src/check_releases.py
python src/ingest.py
python src/audit_staging.py
python src/build_panel.py
python src/package_site.py
```

`check_releases.py` intentionally exits nonzero on unresolved source errors; do not treat a failed daily check as new observations. For historical corrections use `python src/ingest.py --refresh`. Archives download from the SEC inventory. The local staging database is about 1.5 GB, excluded from Git; candidate discovery includes non-equity rows for audit, while production filters use explicit CUSIPs. Full-population amendment/overlap reconciliation remains unfinished. Discovered daily individual filings are queued but not yet merged into the numeric series.

## Hosting and updates

`.github/workflows/research-and-pages.yml` tests and packages the committed dataset on push. Daily/manual runs also check sources, refresh archives/revisions and rebuild the restricted panel. Deployment requires GitHub Pages enabled for GitHub Actions. Failed runs preserve previous deployed data and upload diagnostics. A schedule declaration alone does not establish successful execution; inspect the actual Actions runs. New reporting quarters fail closed until their corporate actions/eligibility are reviewed.

Public JSON includes series, selected manager CIKs, coverage by quarter, archive SHA-256 receipts, per-security price diagnostics and SEC accessions. The dashboard is buildless, mobile responsive, requires no visitor login and can be embedded by iframe once its public deployment is verified.

## Research documentation

* [Methodology](METHODOLOGY.md)
* [Universe and exclusions](UNIVERSE.md)
* [Existing implementation audit](AUDIT.md)
* [Release assessment and limitations](RELEASE_ASSESSMENT.md)

Only this independent repository is written. The existing `VictorHTsai.github.io` and private `victor-investment-os` repositories remain untouched.
