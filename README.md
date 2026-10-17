# AI Institutional Confidence Monitor

**Research in progress. Not a deployed or validated monitor.**

Independent replacement for the preliminary `ai-institutional-ownership` interface. No existing user repositories have been modified.

Start with [AUDIT.md](AUDIT.md), [METHODOLOGY.md](METHODOLOGY.md) and [UNIVERSE.md](UNIVERSE.md).

`python src/ingest.py` downloads official SEC bulk archives listed in `research/archive_urls.json`, records hashes and accession-level metadata, and stages candidate issuer rows in SQLite using Python's standard library. Issuer-name matching is **candidate discovery only**, not a production CUSIP mapping. The staging extract deliberately retains options, old identifiers and principal rows for audit; they must be explicitly filtered and validated downstream. No holdings index or fund-flow estimate is produced by ingestion.

The baseline is a report period, not an archive filename. Future production requires the validation protocol before frontend work or numeric publication. See the gate assessment for exact limitations.
