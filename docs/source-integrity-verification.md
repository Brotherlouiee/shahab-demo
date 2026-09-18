# Canonical source byte verification — US-01.T03a

## Result

All six canonical `.unitext` files were restored from the original supplied file bytes and verified after upload. Each original base64 payload was passed directly to Git's blob API, and Git's returned blob SHA-1 was matched against a local Git-object SHA-1 calculated from the original bytes. Since a Git blob identifier incorporates the literal bytes and their length, equality proves byte-for-byte identity. SHA-256 and byte counts are also recorded. No source was decoded, transcoded, edited, or normalized.

## Accepted evidence

| Source | SHA-256 | Bytes | Result |
| --- | --- | ---: | --- |
| Behavioral questionnaire | `8db132f2147b79f659f51b61754f0d97f0c4ba90c312ae4cca2948770a83accd` | 14,346 | Exact match |
| Loan-variable categories | `29bf4189894e4fc07c656ceee82cd202771af7b30fcc80e732bfca90a583985e` | 1,818 | Exact match |
| Questionnaire-variable mapping | `462185978dd0aeaf4479cf761a092c99d6bccf783cde31645448097577c3fe4e` | 2,366 | Exact match |
| Answer numeric weights | `f786ff278f58a5abb998dafca46625cbf3da5922db1e5c68d505487b57133749` | 35,062 | Exact match |
| Compatibility coefficients | `65859d3de5addef6c164c263100e0fc672897e1518a7b05091ec7b91dbfdcf56` | 10,952 | Exact match |
| Bank-loan database | `598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45` | 211,824 | Exact match |

## Control

The sources retain the requested `.unitext` names but are binary-preserved UTF-16 LE documents. Any later source replacement must use a base64/blob write and repeat this exact comparison before a parser, importer, audit, fixture, scoring rule, or UI can consume the changed source.
