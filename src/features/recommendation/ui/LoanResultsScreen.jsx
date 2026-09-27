import { useEffect, useMemo, useRef, useState } from "react";

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
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR").replaceAll("٬", "/")} تومان`;
}

function formatPercent(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR").replaceAll("٬", "/")}٪`;
}

function formatMonths(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR").replaceAll("٬", "/")} ماه`;
}

function itemsForMode(result, mode) {
  if (!result) return [];
  if (mode === VIEW_MODES.lowest) return result.lowCompatibilityRecommendations;
  if (mode === VIEW_MODES.variable) return result.needsReview;
  return result.rankedRecommendations;
}



function FilterMenu({ label, value, selectedValue, options, onChange }) {
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);
  useEffect(() => {
    const close = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) setOpen(false);
    };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);
  return <div className="hp-loan-filter-menu-wrap" ref={menuRef}>
    <button type="button" className="hp-loan-filter-trigger" aria-haspopup="listbox" aria-expanded={open} aria-label={label} onClick={() => setOpen((current) => !current)}>{value}</button>
    {open ? <div className="hp-loan-filter-menu" role="listbox" aria-label={label}>
      {options.map((option) => <button key={option.value} type="button" role="option" aria-selected={option.value === selectedValue} onClick={() => { onChange(option.value); setOpen(false); }}>{option.label}</button>)}
    </div> : null}
  </div>;
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
  const bankLogoReference = recommendation.bankLogoReference ?? detail?.bankLogoReference;
  const hasScore = typeof recommendation.compatibilityScore === "number";

  return (
    <article className="hp-loan-result-card hp-serving-loan-card">
      <header className="hp-loan-result-head">
        <div>
          {bankLogoReference ? <img src={bankLogoReference} alt={recommendation.lenderName} referrerPolicy="no-referrer" /> : null}
          <span>«{recommendation.lenderName}»</span>
        </div>
        <strong>{recommendation.loanName}</strong>
      </header>

      <p className="hp-loan-match">
        تطابق با وضعیت مشتری: <b>{hasScore ? `${Math.round(recommendation.compatibilityScore * 100).toLocaleString("fa-IR").replaceAll("٬", "/")}٪` : "نامشخص"}</b>
      </p>

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
    <main className="hp-questionnaire-page hp-loan-results-page header-top" dir="rtl" aria-busy={status === "loading"}>
      <div className="hp-loan-results-top">
        {header}
      </div>
      <div className="hp-loan-results-controls">
          <div className="hp-loan-results-actions">
            <button
              className="is-primary"
              type="button"
              disabled
              title="روش اقدام یا ثبت درخواست تأییدشده برای این وام‌ها ثبت نشده است."
            >
              ثبت درخواست همزمان وام بانکی
            </button>
            <button type="button" onClick={() => onCompare(result)} disabled={status !== "ready"}>
              مقایسه وام
            </button>
          </div>

          <div className="hp-loan-result-filters">
            <FilterMenu label="نمایش نتایج" value={VIEW_MODE_LABELS[mode]} selectedValue={mode} options={Object.entries(VIEW_MODE_LABELS).map(([value, label]) => ({ value, label }))} onChange={setMode} />
            <FilterMenu label="نام بانک" value={lenderName || "نام بانک"} selectedValue={lenderName} options={[{ value: "", label: "نام بانک" }, ...lenders.map((name) => ({ value: name, label: name }))]} onChange={setLenderName} />
          </div>
      </div>

      <section className="hp-loan-results-list">
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
