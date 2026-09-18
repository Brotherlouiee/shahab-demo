# Canonical source inventory — US-01.T03

## Scope

This document inventories the six required canonical source files and verifies their identity against the original files supplied for this project. It does not normalize, repair, reinterpret, or alter source data.

## Integrity result — blocking for data implementation

All six expected `.unitext` paths exist on the working branch, but their Git blob identities and byte sizes do **not** match the corresponding original uploaded files. The originals are UTF-16 little-endian text. Therefore, the repository copies cannot yet be treated as verified raw canonical sources for parsing, data audit, scoring, or production use.

The mismatch must be resolved in a dedicated source-preservation task using byte-safe replacement and a post-upload hash comparison. Do not silently use, edit, transcode, or infer data from the current Git copies. This is a blocker for `US-02` and later data/recommendation implementation; it does not invalidate the completed baseline/inventory documentation tasks.

## Source identity table

| Source role | Repository path | Git blob SHA-1 / bytes | Original SHA-256 / bytes | Encoding | Status |
| --- | --- | --- | --- | --- | --- |
| Behavioral question text and option identifiers | `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext` | `c8a8d29a9c0053349ebcf1c912faff4e0ec8dedc` / 15,950 | `8db132f2147b79f659f51b61754f0d97f0c4ba90c312ae4cca2948770a83accd` / 14,346 | UTF-16 LE | Mismatch — blocked |
| Standard categories for eight loan variables | `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext` | `567d2485e9c3e487244556b6a6c8b5ce1780fecd` / 2,250 | `29bf4189894e4fc07c656ceee82cd202771af7b30fcc80e732bfca90a583985e` / 1,818 | UTF-16 LE | Mismatch — blocked |
| Question-to-loan-variable mapping | `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext` | `546018d4f258480857cbd17c2c2f9c2aa8fe670e` / 2,678 | `462185978dd0aeaf4479cf761a092c99d6bccf783cde31645448097577c3fe4e` / 2,366 | UTF-16 LE | Mismatch — blocked |
| Answer-to-numeric-weight mapping | `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext` | `8dbdb9eb84b04aeb80d26c261ace83508cc15e81` / 40,076 | `f786ff278f58a5abb998dafca46625cbf3da5922db1e5c68d505487b57133749` / 35,062 | UTF-16 LE | Mismatch — blocked |
| One-to-one answer/category compatibility coefficients | `.agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext` | `3b87af3ac09775a0e94a398e82a9ec85afc871b4` / 12,332 | `65859d3de5addef6c164c263100e0fc672897e1518a7b05091ec7b91dbfdcf56` / 10,952 | UTF-16 LE | Mismatch — blocked |
| Raw bank-loan database and display conditions | `.agents/documents/دیتابیس وام های بانکی.unitext` | `cd9f9acbb3b3901e0ab0615272a60a9be3330e67` / 224,414 | `598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45` / 211,824 | UTF-16 LE | Mismatch — blocked |

## Required resolution gate

1. Replace each repository `.unitext` file from its original bytes, preserving UTF-16 LE and line endings.
2. Record SHA-256 and byte count for both the supplied original and the repository copy after replacement.
3. Require exact equality for each of the six source files before declaring the source inventory verified.
4. Only then start `US-02.T01` or any importer, parser, data-audit, fixture, score, UI mapping, or database import work.

## Golden-rule attestation

1. This is one incremental documentation task; no deploy or data transformation occurred.
2. The complete canonical guide was reread before execution.
3. The task is closed only with this inventory, current-state/CHANGELOG updates, a baseline build verification, and a dedicated commit.
