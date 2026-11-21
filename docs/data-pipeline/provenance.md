# Canonical-source provenance — US-02.T03

The audit reads the six verified UTF-16 LE canonical sources without changing them. For each run, `scripts/data_audit.py` records the repository target path, exact input path, encoding, SHA-256, byte count and row count in `docs/data-audit/report.v1.json`.

The audit report is evidence, not a serving-data artifact. It must be regenerated from verified raw source bytes before every source import or data-decision review. A changed hash creates a new provenance version and requires review; no parser, import, score, or UI output may silently reuse an obsolete report.

Run locally from the repository root with:

```bash
python scripts/data_audit.py --source-dir /path/to/verified-sources --output docs/data-audit/report.v1.json
```

The project’s canonical repository paths use `.unitext`; the initial audit run uses the byte-identical uploaded originals as its verified local source directory.
