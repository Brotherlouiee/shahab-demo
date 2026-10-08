import { Fragment, useEffect, useMemo, useRef, useState } from "react";

import BankIdentity from "../../loan-details/BankIdentity.jsx";
import { fetchLoanDetails } from "../../loan-details/loanDetailsApi.js";
import LoanPercent from "../../loan-details/LoanPercent.jsx";
import { toPersianDigits } from "../../loan-details/toPersianDigits.mjs";
import { compatibilityBandForScore } from "./compatibilityDisplay.mjs";
import { displayItemsForResultMode } from "../presentation/loanResultDisplayOrder.mjs";
import DeferredPageSkeleton from "../../../shared/DeferredPageSkeleton.jsx";
import { readSavedLoans, toggleSavedLoan } from "../../account/savedLoans.mjs";

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

function formatMonths(value) {
  return value == null ? "اعلام نشده" : `${Number(value).toLocaleString("fa-IR").replaceAll("٬", "/")} ماه`;
}

function BookmarkSaveIcon({ filled }) {
  const assetUrl = filled ? "/ui-icons/save-bold.png" : "/ui-icons/save-linear.png";
  return <img src={assetUrl} alt="" aria-hidden="true" />;
}

function FilterMenu({ label, value, selectedValue, options, onChange, scrollable = false }) {
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
    {open ? <div className={`hp-loan-filter-menu${scrollable ? " is-scrollable" : ""}`} role="listbox" aria-label={label}>
      {options.map((option) => <button key={option.value} type="button" role="option" aria-selected={option.value === selectedValue} onClick={() => { onChange(option.value); setOpen(false); }}>{option.label}</button>)}
    </div> : null}
  </div>;
}

/**
 * One real serving-loan card. All monetary facts and logo URLs are fetched from
 * the approved loan-detail API; this component never synthesizes loan facts.
 */
function ServingLoanCard({ recommendation, onDetails, isSaved, onSave }) {
  const [state, setState] = useState(() => recommendation.loanSummary
    ? { status: "ready", detail: recommendation.loanSummary }
    : { status: "loading", detail: null });

  useEffect(() => {
    // Use the real card facts included with the PUBLISHED recommendation.
    // Full conditions remain lazy on the dedicated details route.
    if (recommendation.loanSummary) {
      setState({ status: "ready", detail: recommendation.loanSummary });
      return undefined;
    }
    const controller = new AbortController();
    setState({ status: "loading", detail: null });
    fetchLoanDetails(recommendation.loanId, { signal: controller.signal })
      .then((detail) => setState({ status: detail ? "ready" : "empty", detail }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ status: "error", detail: null });
      });
    return () => controller.abort();
  }, [recommendation.loanId, recommendation.loanSummary]);

  const detail = state.detail;
  const hasScore = typeof recommendation.compatibilityScore === "number";
  const compatibilityBand = compatibilityBandForScore(recommendation.compatibilityScore);

  return (
    <article className="hp-loan-result-card hp-serving-loan-card" data-compatibility-band={compatibilityBand || undefined}>
      <header className="hp-loan-result-head">
        <BankIdentity lenderName={recommendation.lenderName} />
        <strong title={toPersianDigits(recommendation.loanName)} aria-label={toPersianDigits(recommendation.loanName)}>{toPersianDigits(recommendation.loanName)}</strong>
      </header>

      <div className="hp-loan-match-row">
        <p className="hp-loan-match">
          تطابق با وضعیت مشتری: <b>{hasScore ? <LoanPercent value={Math.round(recommendation.compatibilityScore * 100)} /> : "نامشخص"}</b>
        </p>
        <button
          className="hp-loan-save-button"
          type="button"
          aria-pressed={isSaved}
          aria-label={`ذخیره وام ${toPersianDigits(recommendation.loanName)}`}
          title="ذخیره وام"
          onClick={() => onSave(recommendation.loanId)}
        >
          <BookmarkSaveIcon filled={isSaved} />
        </button>
      </div>

      {state.status === "ready" ? (
        <div className="hp-loan-summary-grid">
          <span>حداکثر مبلغ وام</span><b>{formatMoney(detail.maxAmountTomans)}</b>
          <span>نرخ بهره اعلامی</span><b><LoanPercent value={detail.interestRatePercent} /></b>
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
 * partitions and filters lender identity. Low-compatibility cards are presented
 * in descending order using their already server-supplied score; it never calculates a score.
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
  const [savedLoanIds, setSavedLoanIds] = useState(() => new Set(readSavedLoans().map((loan) => loan.loanId)));
  const [savedToastLoanId, setSavedToastLoanId] = useState(null);
  const saveToastTimeoutRef = useRef(null);

  useEffect(() => () => window.clearTimeout(saveToastTimeoutRef.current), []);

  const handleSavedLoan = (recommendation) => {
    const loanId = recommendation.loanId;
    const wasSaved = savedLoanIds.has(loanId);
    toggleSavedLoan(recommendation);
    setSavedLoanIds(new Set(readSavedLoans().map((loan) => loan.loanId)));

    window.clearTimeout(saveToastTimeoutRef.current);
    if (wasSaved) {
      setSavedToastLoanId(null);
      return;
    }

    setSavedToastLoanId(loanId);
    saveToastTimeoutRef.current = window.setTimeout(() => setSavedToastLoanId(null), 2000);
  };

  const items = useMemo(() => displayItemsForResultMode(result, mode), [result, mode]);
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
              بررسی آمادگی دریافت وام
            </button>
            <button type="button" onClick={() => onCompare(result)} disabled={status !== "ready"}>
              مقایسه وام
            </button>
          </div>

          <div className="hp-loan-result-filters">
            <FilterMenu label="نمایش نتایج" value={VIEW_MODE_LABELS[mode]} selectedValue={mode} options={Object.entries(VIEW_MODE_LABELS).map(([value, label]) => ({ value, label }))} onChange={setMode} />
            <FilterMenu label="نام بانک" value={lenderName || "نام بانک"} selectedValue={lenderName} options={[{ value: "", label: "نام بانک" }, ...lenders.map((name) => ({ value: name, label: name }))]} onChange={setLenderName} scrollable={lenders.length > 4} />
          </div>
      </div>

      <section className="hp-loan-results-list">
        <DeferredPageSkeleton active={status === "loading"} variant="cards" />
        {status === "sessionMissing" ? (
          <div className="hp-recommendation-result-state" role="status">
            <p>برای دیدن نتیجه، ابتدا پرسشنامه را در همین تب کامل کنید.</p>
            <button type="button" onClick={onStartQuestionnaire}>شروع پرسشنامه</button>
          </div>
        ) : null}
        {status === "error" ? <div className="hp-recommendation-result-state" role="alert"><p>دریافت نتیجه در حال حاضر ممکن نیست.</p><button type="button" onClick={onRetry}>تلاش مجدد</button></div> : null}
        {status === "ready" && !visibleItems.length ? <p className="hp-recommendation-result-state">برای این فیلتر نتیجه‌ای موجود نیست.</p> : null}
        {status === "ready" ? visibleItems.map((item) => (
          <Fragment key={item.loanId}>
            {savedToastLoanId === item.loanId ? (
              <p className="hp-loan-save-toast" role="status" aria-live="polite">وام مورد نظر با موفقیت ذخیره شد</p>
            ) : null}
            <ServingLoanCard
              recommendation={item}
              onDetails={onDetails}
              isSaved={savedLoanIds.has(item.loanId)}
              onSave={() => handleSavedLoan(item)}
            />
          </Fragment>
        )) : null}
      </section>
    </main>
  );
}

export { displayItemsForResultMode as itemsForMode };
