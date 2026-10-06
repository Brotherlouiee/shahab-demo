# US-09.T06M local evidence

These measurements use the real local Docker API through port 4173 and synthetic questionnaire inputs. They verify local behavior, not a deployed staging environment.

| Evidence | Result |
| --- | --- |
| Baseline footer | Sticky bar bottom 1272.375 px for a 720 px viewport; below the initial view. |
| Final footer | Fixed bar/button bottom 720 px on desktop and 844 px on mobile. |
| Recommendation scheduling | Request starts during the preserved five-second analysis countdown, rather than after it. |
| Final analysis-to-results | 5497 ms, overlapping a 2858 ms API response. |
| Initial analysis-logo requests | Zero; the 25 original imports load only for analysis. |
| Interactive questionnaire | 3430 ms; all resources finished at 4572 ms. |
| Interactive published detail | 1500 ms. |
| Real recommendation partitions | 7 ranked, 81 low-compatibility, 14 needs-review; unchanged. |

`baseline.json`, `after-first-run.json` and `after-final.json` contain observed real response times. These runs had different load/cache conditions: they establish correctness and overlap, not a controlled percentage speedup. Full-flow `firstQuestionReadyMs` waits for the browser load event; `interactive-readiness.json` separately measures usable UI after DOMContentLoaded.

The screenshots show the actual published loan detail and bottom CTA at desktop/mobile sizes, including the final condition after scrolling. The controlled browser tests also hold a recommendation response open past the countdown, return an error until explicit retry, and hold the external font stylesheet open while the questionnaire stays usable.

Known limits: cold Docker/Vite and API latency remain environment-dependent; the five-second countdown is intentionally preserved. A very slow server still shows the honest loading state. Font loading can briefly use the existing fallback. No dependency, data, backend, provider or deployment changes are included.
