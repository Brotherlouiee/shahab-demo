# Canonical source inventory — US-01.T03

## Scope

This document inventories the six required canonical source files and verifies their identity against the original files supplied for this project. It does not normalize, repair, reinterpret, or alter source data.

## Integrity result — verified in US-01.T03a

The six expected `.unitext` paths were restored from the original supplied bytes in `US-01.T03a`. The originals are UTF-16 little-endian text, and the repository copies were written with a byte-safe base64 Git-blob operation; no decoding, transcoding, normalization, or line-ending conversion was applied.

For every source, the exact original base64 payload is sent to Git's blob API and the returned Git blob identifier is compared with the Git blob identifier calculated locally from the original bytes. This is a byte-identity proof: Git computes that identifier from the literal blob bytes, including the byte count. SHA-256 and byte counts are also recorded below. The former source-integrity blocker is resolved. These files may now be used as the verified raw canonical sources in `US-02`, subject to the separate data-audit and decision gates in the canonical guide.

## Source identity table

| Source role | Repository path | Verified SHA-256 / bytes | Encoding | Status |
| --- | --- | --- | --- | --- |
| Behavioral question text and option identifiers | `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext` | `8db132f2147b79f659f51b61754f0d97f0c4ba90c312ae4cca2948770a83accd` / 14,346 | UTF-16 LE | Verified |
| Standard categories for eight loan variables | `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext` | `29bf4189894e4fc07c656ceee82cd202771af7b30fcc80e732bfca90a583985e` / 1,818 | UTF-16 LE | Verified |
| Question-to-loan-variable mapping | `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext` | `462185978dd0aeaf4479cf761a092c99d6bccf783cde31645448097577c3fe4e` / 2,366 | UTF-16 LE | Verified |
| Answer-to-numeric-weight mapping | `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext` | `f786ff278f58a5abb998dafca46625cbf3da5922db1e5c68d505487b57133749` / 35,062 | UTF-16 LE | Verified |
| One-to-one answer/category compatibility coefficients | `.agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext` | `65859d3de5addef6c164c263100e0fc672897e1518a7b05091ec7b91dbfdcf56` / 10,952 | UTF-16 LE | Verified |
| Raw bank-loan database and display conditions | `.agents/documents/دیتابیس وام های بانکی.unitext` | `598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45` / 211,824 | UTF-16 LE | Verified |

## Verification evidence and future preservation rule

1. Repository sources are stored with the `.unitext` suffix, while their original UTF-16 LE bytes and line endings are retained exactly.
2. Every future edit or replacement must use a binary/base64 Git operation and repeat the source SHA-256 and byte-count comparison before use.
3. `US-02.T01` may start only after `US-01` itself has completed its remaining tasks and gates; source integrity is no longer the blocking condition.

## Golden-rule attestation

1. This is one incremental documentation task; no deploy or data transformation occurred.
2. The complete canonical guide was reread before execution.
3. `US-01.T03a` is closed only with byte-equality proof, current-state/CHANGELOG updates, a baseline build verification, and a dedicated commit.
