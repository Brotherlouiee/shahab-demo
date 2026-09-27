import { useEffect, useMemo, useState } from "react";

import { fetchLoanDetails } from "../../loan-details/loanDetailsApi.js";

const VIEW_MODES = Object.freeze({
  highest: "highest",
  lowest: "lowest",
  variable: "variable",
});

const VIEW_MODE_LABELS = Object.freeze({
  [VIEW_MODES.highest]: "بیشترین تطابق",
  [VIEW_MODES.lowest]: "کمترین تطابق",
  [VIEW_MODES.variable]: "وضعیت متغیر",
});

function formatMoney(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR")} تومان`;
}

function formatPercent(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR")}٪`;
}

function formatMonths(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR")} ماه`;
}

function itemsForMode(result, mode) {
  if (!result) return [];
  if (mode === VIEW_MODES.lowest) return result.lowCompatibilityRecommendations;
  if (mode === VIEW_MODES.variable) return result.needsReview;
  return result.rankedRecommendations;
}

/**
 * One real serving-loan card. All monetary facts and logo URLs are fetched from
 * the approved loan-detail API; this component never synthesizes loan facts.
 */
function ServingLoanCard({ recommendation, onDetails }) {
  const [state, setState] = useState({ status: "loading", detail: null });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading", detail: null });
    fetchLoanDetails(recommendation.loanId, { signal: controller.signal })
      .then((detail) => setState({ status: detail ? "ready" : "empty", detail }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ status: "error", detail: null });
      });
    return () => controller.abort();
  }, [recommendation.loanId]);

  const detail = state.detail;
  const hasScore = typeof recommendation.compatibilityScore === "number";

  return (
    <article className="hp-loan-result-card hp-serving-loan-card">
      <header className="hp-loan-result-head">
        <div>
          {detail?.bankLogoReference ? <img src={detail.bankLogoReference} alt={recommendation.lenderName} /> : null}
          <span>«{recommendation.lenderName}»</span>
        </div>
        <strong>{recommendation.loanName}</strong>
      </header>

      {hasScore ? (
        <p className="hp-loan-match">
          تطابق با وضعیت مشتری: <b><span dir="ltr">{Math.round(recommendation.compatibilityScore * 100).toLocaleString("fa-IR")}٪</span></b>
        </p>
      ) : <p className="hp-recommendation-warning">وضعیت متغیر؛ بدون درصد و رتبه</p>}
      {recommendation.statusLabel ? <p className="hp-recommendation-warning">{recommendation.statusLabel}</p> : null}
      {recommendation.compatibilityReason ? <p className="hp-recommendation-reason">{recommendation.compatibilityReason}</p> : null}
      {recommendation.rankingExcludedReasons?.length ? <p className="hp-recommendation-reason">{recommendation.rankingExcludedReasons.join("، ")}</p> : null}

      {state.status === "loading" ? <p className="hp-loan-card-loading">در حال دریافت شرایط وام…</p> : null}
      {state.status === "error" ? <p className="hp-loan-card-loading">جزئیات این وام فعلاً در دسترس نیست.</p> : null}
      {state.status === "ready" ? (
        <div className="hp-loan-summary-grid">
          <span>حداکثر مبلغ وام</span><b>{formatMoney(detail.maxAmountTomans)}</b>
          <span>نرخ بهره اعلامی</span><b>{formatPercent(detail.interestRatePercent)}</b>
          <span>مبلغ هر قسط</span><b>{formatMoney(detail.monthlyInstallmentTomans)}</b>
          <span>حداکثر زمان بازپرداخت</span><b>{formatMonths(detail.maxRepaymentMonths)}</b>
        </div>
      ) : null}

      <a
        className="hp-loan-docs-link"
        href={`/loan-details?loanId=${encodeURIComponent(recommendation.loanId)}`}
        onClick={(event) => {
          event.preventDefault();
          onDetails(recommendation.loanId);
        }}
      >
        مشاهده شرایط و مدارک مورد نیاز
      </a>
    </article>
  );
}

/**
 * Result screen extracted from home page. It only selects server-owned
 * partitions and filters lender identity; it never calculates or reorders a
 * compatibility score.
 */
export default function LoanResultsScreen({
  result,
  status,
  onRetry,
  onStartQuestionnaire,
  header,
  onDetails,
  onCompare,
  onRequest,
}) {
  const [mode, setMode] = useState(VIEW_MODES.highest);
  const [lenderName, setLenderName] = useState("");

  const items = useMemo(() => itemsForMode(result, mode), [result, mode]);
  const lenders = useMemo(
    () => [...new Set(items.map((item) => item.lenderName))].sort(new Intl.Collator("fa").compare),
    [items],
  );
  const visibleItems = useMemo(
    () => items.filter((item) => !lenderName || item.lenderName === lenderName),
    [items, lenderName],
  );

  useEffect(() => {
    if (lenderName && !lenders.includes(lenderName)) setLenderName("");
  }, [lenderName, lenders]);

  return (
    <main className="hp-questionnaire-page hp-loan-results-page" dir="rtl" aria-busy={status === "loading"}>
      <div className="hp-loan-results-top">
        {header}
        <div className="hp-loan-results-controls">
          <div className="hp-loan-results-actions">
            <button className="is-primary" type="button" onClick={() => onRequest(result)} disabled={status !== "ready"}>
              ثبت درخواست همزمان وام بانکی
            </button>
            <button type="button" onClick={() => onCompare(result)} disabled={status !== "ready"}>
              مقایسه وام
            </button>
          </div>

          <div className="hp-loan-result-filters">
            <label>
              <span className="sr-only">نمایش نتایج</span>
              <select value={mode} onChange={(event) => setMode(event.target.value)}>
                {Object.entries(VIEW_MODE_LABELS).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </label>
            <label>
              <span className="sr-only">نام بانک</span>
              <select value={lenderName} onChange={(event) => setLenderName(event.target.value)}>
                <option value="">نام بانک</option>
                {lenders.map((name) => <option key={name} value={name}>{name}</option>)}
              </select>
            </label>
          </div>
        </div>
      </div>

      <section className={`hp-loan-results-list ${mode === VIEW_MODES.variable ? "hp-recommendation-needs-review" : ""}`}>
        {status === "loading" ? <p className="hp-recommendation-result-state" role="status">در حال دریافت نتیجه…</p> : null}
        {status === "sessionMissing" ? (
          <div className="hp-recommendation-result-state" role="status">
            <p>برای دیدن نتیجه، ابتدا پرسشنامه را در همین تب کامل کنید.</p>
            <button type="button" onClick={onStartQuestionnaire}>شروع پرسشنامه</button>
          </div>
        ) : null}
        {status === "error" ? <div className="hp-recommendation-result-state" role="alert"><p>دریافت نتیجه در حال حاضر ممکن نیست.</p><button type="button" onClick={onRetry}>تلاش مجدد</button></div> : null}
        {status === "ready" && !visibleItems.length ? <p className="hp-recommendation-result-state">برای این فیلتر نتیجه‌ای موجود نیست.</p> : null}
        {status === "ready" ? visibleItems.map((item) => <ServingLoanCard key={item.loanId} recommendation={item} onDetails={onDetails} />) : null}
      </section>
    </main>
  );
}

export { itemsForMode };
