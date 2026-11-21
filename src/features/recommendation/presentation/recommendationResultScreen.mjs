import { createElement as h, useMemo, useState } from "react";

import {
  formatServerCompatibilityScore,
  recommendationResultControlOptions,
  selectRecommendationResultMode,
} from "./recommendationResultControls.mjs";

const MODE_COPY = Object.freeze({
  highest: { label: "بیشترین تطابق", title: "پیشنهادهای دارای بیشترین تطابق", empty: "در حال حاضر وامی بالاتر از آستانهٔ پیشنهاد وجود ندارد." },
  lowest: { label: "کمترین تطابق", title: "وام‌های دارای تطابق پایین", empty: "وام دارای score معتبر زیر آستانه وجود ندارد." },
  variable: { label: "وضعیت متغیر", title: "گزینه‌هایی که برای مقایسهٔ دقیق به اطلاعات بیشتری نیاز دارند", empty: "وام نیازمند بررسی بیشتری وجود ندارد." },
});

/** RTL presentation of three server-owned recommendation partitions. */
export default function RecommendationResultScreen({
  result, status = "ready", header = null, onRetry, onDetails, onCompare,
  onAction, onAnalysis, onStartQuestionnaire, initialMode = recommendationResultControlOptions.resultModes.highest,
}) {
  const [mode, setMode] = useState(initialMode);
  const items = useMemo(
    () => status === "ready" && result ? selectRecommendationResultMode(result, mode) : [],
    [mode, result, status],
  );

  return h("main", {
    className: "hp-questionnaire-page hp-recommendation-results-screen", dir: "rtl",
    "aria-busy": status === "loading", "aria-labelledby": "recommendation-results-title",
  },
  header,
  h("header", { className: "hp-recommendation-results-heading" },
    h("h1", { id: "recommendation-results-title" }, "نتیجهٔ مقایسهٔ وام‌ها"),
    h("p", null, "درصد تطابق، مقایسهٔ شرایط وام با ترجیحات شماست و به‌معنای تأیید دریافت وام نیست."),
  ),
  status === "sessionMissing"
    ? h("section", { className: "hp-recommendation-result-state", role: "status" },
        h("p", null, "برای دیدن نتیجه، ابتدا پرسشنامه را در همین تب کامل کنید. نشست معتبر یا پاسخ کامل در دسترس نیست."),
        h("button", { type: "button", onClick: onStartQuestionnaire }, "شروع پرسشنامه"),
      ) : null,
  status === "loading"
    ? h("section", { className: "hp-recommendation-result-state", role: "status", "aria-live": "polite" }, "در حال دریافت نتیجه…") : null,
  status === "error"
    ? h("section", { className: "hp-recommendation-result-state", role: "alert" },
        h("p", null, "دریافت نتیجه در حال حاضر ممکن نیست."),
        typeof onRetry === "function" ? h("button", { type: "button", onClick: onRetry }, "تلاش مجدد") : null,
      ) : null,
  status === "ready" && result
    ? h(ReadyResult, { items, mode, result, setMode, onDetails, onCompare, onAction, onAnalysis }) : null);
}

function ReadyResult({ items, mode, result, setMode, onDetails, onCompare, onAction, onAnalysis }) {
  const modeCopy = MODE_COPY[mode];
  return h("div", { className: "hp-recommendation-results-content" },
    h("div", { className: "hp-loan-results-actions" },
      h("button", { type: "button", onClick: () => onCompare?.(result) }, "مقایسه وام"),
      h("button", { type: "button", onClick: () => onAction?.(result) }, "روش اقدام یا درخواست"),
    ),
    h("div", { className: "hp-recommendation-result-filters", role: "group", "aria-label": "نوع نتیجه" },
      ...Object.entries(MODE_COPY).map(([value, copy]) => h("button", {
        key: value, type: "button", className: mode === value ? "is-active" : "",
        "aria-pressed": mode === value, onClick: () => setMode(value),
      }, copy.label)),
    ),
    h("p", { className: "hp-recommendation-result-announcement", role: "status", "aria-live": "polite" },
      items.length ? `${items.length.toLocaleString("fa-IR")} گزینه نمایش داده می‌شود.` : modeCopy.empty,
    ),
    items.length
      ? h("section", { className: `hp-recommendation-section ${mode === "variable" ? "hp-recommendation-needs-review" : ""}` },
          h("h2", null, modeCopy.title),
          h("div", { className: "hp-recommendation-result-list" },
            ...items.map((item) => mode === "variable"
              ? h(NeedsReviewCard, { key: item.loanId, item, onDetails, onAnalysis })
              : h(ScoredCard, { key: item.loanId, item, low: mode === "lowest", onDetails, onAnalysis }))),
        )
      : h("section", { className: "hp-recommendation-result-state" }, modeCopy.empty));
}

function ScoredCard({ item, low, onDetails, onAnalysis }) {
  return h("article", { className: "hp-loan-result-card hp-recommendation-result-card" },
    h("header", { className: "hp-loan-result-head" }, h("span", null, `«${item.lenderName}»`), h("h3", null, item.loanName)),
    low ? h("p", { className: "hp-recommendation-warning" }, item.statusLabel) : null,
    h("p", { className: "hp-recommendation-score" }, h("span", null, item.scoreCaption), h("strong", { dir: "ltr" }, formatServerCompatibilityScore(item.compatibilityScore))),
    h("p", { className: "hp-recommendation-reason" }, item.compatibilityReason),
    h("a", { className: "hp-loan-docs-link", href: item.detailsHref, onClick: detailClick(onDetails, item.loanId) }, "مشاهدهٔ جزئیات، شرایط و مدارک"),
    h("button", { className: "hp-loan-docs-link", type: "button", onClick: () => onAnalysis?.(item.loanId) }, "توضیح این نتیجه"));
}

function NeedsReviewCard({ item, onDetails, onAnalysis }) {
  return h("article", { className: "hp-loan-result-card hp-recommendation-result-card" },
    h("header", { className: "hp-loan-result-head" }, h("span", null, `«${item.lenderName}»`), h("h3", null, item.loanName)),
    h("p", { className: "hp-recommendation-warning" }, item.warning),
    h("ul", null, ...item.rankingExcludedReasons.map((reason) => h("li", { key: reason }, reason))),
    h("a", { className: "hp-loan-docs-link", href: item.detailsHref, onClick: detailClick(onDetails, item.loanId) }, "مشاهدهٔ جزئیات، شرایط و مدارک"),
    h("button", { className: "hp-loan-docs-link", type: "button", onClick: () => onAnalysis?.(item.loanId) }, "توضیح وضعیت"));
}

function detailClick(onDetails, loanId) {
  if (typeof onDetails !== "function") return undefined;
  return (event) => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    onDetails(loanId);
  };
}
