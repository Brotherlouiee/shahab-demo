import { createElement as h, useMemo, useState } from "react";

import {
  applyRecommendationResultControls,
  formatServerCompatibilityScore,
  recommendationResultControlOptions,
} from "./recommendationResultControls.mjs";
import { buildRecommendationResultDisplayState } from "./recommendationResultStates.mjs";

/**
 * RTL and accessible presentation boundary for a validated server result.
 *
 * Data fetching and session handling deliberately remain outside this component.
 * T06 will connect it to the live API; this screen never creates static loans or
 * calculates a recommendation score.
 */
export default function RecommendationResultScreen({
  result,
  status = "ready",
  header = null,
  onRetry,
}) {
  const [lenderName, setLenderName] = useState(recommendationResultControlOptions.allLenders);
  const [sort, setSort] = useState(recommendationResultControlOptions.sorts.serverOrder);

  const controls = useMemo(
    () => status === "ready" && result
      ? applyRecommendationResultControls(result, { lenderName, sort })
      : null,
    [result, status, lenderName, sort],
  );
  const displayState = useMemo(
    () => controls
      ? buildRecommendationResultDisplayState(result, {
          hasManualFilters: controls.hasManualFilters,
          visibleRankedRecommendations: controls.filteredRankedRecommendations,
        })
      : null,
    [controls, result],
  );

  return h(
    "main",
    {
      className: "hp-questionnaire-page hp-recommendation-results-screen",
      dir: "rtl",
      "aria-busy": status === "loading",
      "aria-labelledby": "recommendation-results-title",
    },
    header,
    h("header", { className: "hp-recommendation-results-heading" },
      h("h1", { id: "recommendation-results-title" }, "نتیجهٔ مقایسهٔ وام‌ها"),
      h("p", null, "درصد تطابق، مقایسهٔ شرایط وام با ترجیحات شماست و به‌معنای تأیید دریافت وام نیست."),
    ),
    status === "loading"
      ? h("section", { className: "hp-recommendation-result-state", role: "status", "aria-live": "polite" }, "در حال دریافت نتیجه…")
      : null,
    status === "error"
      ? h("section", { className: "hp-recommendation-result-state", role: "alert" },
          h("p", null, "دریافت نتیجه در حال حاضر ممکن نیست."),
          typeof onRetry === "function"
            ? h("button", { type: "button", onClick: onRetry }, "تلاش مجدد")
            : null,
        )
      : null,
    status === "ready" && controls && displayState
      ? h(ReadyRecommendationResult, {
          controls,
          displayState,
          onLenderNameChange: setLenderName,
          onSortChange: setSort,
        })
      : null,
  );
}

function ReadyRecommendationResult({
  controls,
  displayState,
  onLenderNameChange,
  onSortChange,
}) {
  return h(
    "div",
    { className: "hp-recommendation-results-content" },
    h("form", { className: "hp-recommendation-result-filters", onSubmit: preventSubmit },
      h("div", null,
        h("label", { htmlFor: "recommendation-lender-filter" }, "نام بانک"),
        h(
          "select",
          {
            id: "recommendation-lender-filter",
            value: controls.lenderName,
            onChange: (event) => onLenderNameChange(event.target.value),
          },
          h("option", { value: recommendationResultControlOptions.allLenders }, "همهٔ بانک‌ها"),
          ...controls.availableLenders.map((name) => h("option", { key: name, value: name }, name)),
        ),
      ),
      h("div", null,
        h("label", { htmlFor: "recommendation-sort" }, "مرتب‌سازی نمایش"),
        h(
          "select",
          {
            id: "recommendation-sort",
            value: controls.sort,
            onChange: (event) => onSortChange(event.target.value),
          },
          h("option", { value: recommendationResultControlOptions.sorts.serverOrder }, "ترتیب پیشنهادی سامانه"),
          h("option", { value: recommendationResultControlOptions.sorts.lenderNameAsc }, "نام بانک (الفبا)"),
        ),
      ),
    ),
    h(
      "p",
      { className: "hp-recommendation-result-announcement", role: "status", "aria-live": "polite" },
      controls.orderedRankedRecommendations.length
        ? `${controls.orderedRankedRecommendations.length.toLocaleString("fa-IR")} گزینهٔ قابل مقایسه نمایش داده می‌شود.`
        : displayState.emptyState?.message,
    ),
    displayState.ranked
      ? h(RecommendationSection, {
          title: displayState.ranked.title,
          items: controls.orderedRankedRecommendations,
        })
      : null,
    displayState.emptyState && displayState.emptyState.kind !== "zeroAfterFilter"
      ? h("section", { className: "hp-recommendation-result-state", role: "status" }, displayState.emptyState.message)
      : null,
    displayState.needsReview
      ? h(NeedsReviewSection, { section: displayState.needsReview })
      : null,
  );
}

function RecommendationSection({ title, items }) {
  return h(
    "section",
    { className: "hp-recommendation-section", "aria-labelledby": "ranked-recommendations-title" },
    h("h2", { id: "ranked-recommendations-title" }, title),
    h("div", { className: "hp-recommendation-result-list" },
      ...items.map((item) => h(RecommendationCard, { key: item.loanId, item })),
    ),
  );
}

function RecommendationCard({ item }) {
  return h(
    "article",
    { className: "hp-loan-result-card hp-recommendation-result-card" },
    h("header", { className: "hp-loan-result-head" },
      h("span", null, `«${item.lenderName}»`),
      h("h3", null, item.loanName),
    ),
    h("p", { className: "hp-recommendation-score" },
      h("span", null, item.scoreCaption),
      h("strong", { dir: "ltr" }, formatServerCompatibilityScore(item.compatibilityScore)),
    ),
    h("p", { className: "hp-recommendation-reason" }, item.compatibilityReason),
    h("a", { className: "hp-loan-docs-link", href: item.detailsHref }, "مشاهدهٔ جزئیات، شرایط و مدارک"),
  );
}

function NeedsReviewSection({ section }) {
  return h(
    "section",
    { className: "hp-recommendation-section hp-recommendation-needs-review", "aria-labelledby": "needs-review-title" },
    h("h2", { id: "needs-review-title" }, section.title),
    h("div", { className: "hp-recommendation-result-list" },
      ...section.items.map((item) => h(
        "article",
        { className: "hp-loan-result-card hp-recommendation-result-card", key: item.loanId },
        h("header", { className: "hp-loan-result-head" },
          h("span", null, `«${item.lenderName}»`),
          h("h3", null, item.loanName),
        ),
        h("p", { className: "hp-recommendation-warning" }, item.warning),
        h("a", { className: "hp-loan-docs-link", href: item.detailsHref }, "مشاهدهٔ جزئیات، شرایط و مدارک"),
      )),
    ),
  );
}

function preventSubmit(event) {
  event.preventDefault();
}
