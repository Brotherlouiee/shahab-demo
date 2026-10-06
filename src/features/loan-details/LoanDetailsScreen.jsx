import { useEffect, useState } from "react";

import BankIdentity from "./BankIdentity.jsx";
import { fetchLoanDetails } from "./loanDetailsApi";
import LoanPercent from "./LoanPercent.jsx";
import { toPersianDigits } from "./toPersianDigits.mjs";

function formatNumber(value) {
  return value === null || value === undefined ? "اعلام نشده" : Number(value).toLocaleString("fa-IR").replaceAll("٬", "/");
}

function DetailValue({ label, children }) {
  return <><span>{label}</span><b>{children}</b></>;
}

function DetailGroup({ children }) {
  return <div className="hp-loan-detail-group">{children}</div>;
}

/** Render API-approved facts as text; neither source text nor error payloads become HTML. */
export default function LoanDetailsScreen({ loanId, header, onAiAnalysis }) {
  const [state, setState] = useState({ status: "loading", detail: null });
  const [requestVersion, setRequestVersion] = useState(0);

  useEffect(() => {
    if (!loanId) {
      setState({ status: "empty", detail: null });
      return undefined;
    }
    const controller = new AbortController();
    setState({ status: "loading", detail: null });
    fetchLoanDetails(loanId, { signal: controller.signal })
      .then((detail) => setState(detail ? { status: "ready", detail } : { status: "empty", detail: null }))
      .catch((error) => {
        if (error.name !== "AbortError") setState({ status: "error", detail: null });
      });
    return () => controller.abort();
  }, [loanId, requestVersion]);

  return (
    <main className="hp-questionnaire-page hp-loan-details-page" dir="rtl" aria-busy={state.status === "loading"}>
      {header}
      {state.status === "loading" ? <section className="hp-loan-details-state" role="status">در حال دریافت جزئیات وام…</section> : null}
      {state.status === "empty" ? <section className="hp-loan-details-state">جزئیات این وام در فهرست تأییدشده موجود نیست.</section> : null}
      {state.status === "error" ? (
        <section className="hp-loan-details-state" role="alert">
          <p>دریافت جزئیات وام در حال حاضر ممکن نیست.</p>
          <button type="button" onClick={() => setRequestVersion((value) => value + 1)}>تلاش مجدد</button>
        </section>
      ) : null}
      {state.status === "ready" ? <LoanDetail detail={state.detail} onAiAnalysis={onAiAnalysis} /> : null}
    </main>
  );
}

function LoanDetail({ detail, onAiAnalysis }) {
  return <>
    <article className="hp-loan-result-card is-details hp-loan-detail-card">
      <div className="hp-loan-result-head">
        <BankIdentity lenderName={detail.lenderName} />
        <strong title={toPersianDigits(detail.loanName)} aria-label={toPersianDigits(detail.loanName)}>{toPersianDigits(detail.loanName)}</strong>
      </div>
      <div className="hp-loan-detail-groups" aria-label="مشخصات تأییدشدهٔ وام">
        <DetailGroup>
          <DetailValue label="حداکثر مبلغ وام">{formatNumber(detail.maxAmountTomans)} تومان</DetailValue>
          <DetailValue label="نرخ بهره اعلامی"><LoanPercent value={detail.interestRatePercent} /></DetailValue>
        </DetailGroup>
        <DetailGroup>
          <DetailValue label="مبلغ هر قسط">{formatNumber(detail.monthlyInstallmentTomans)} تومان</DetailValue>
          <DetailValue label="حداکثر زمان بازپرداخت">{detail.maxRepaymentMonths === null ? "اعلام نشده" : `${formatNumber(detail.maxRepaymentMonths)} ماه`}</DetailValue>
        </DetailGroup>
        <DetailGroup>
          <DetailValue label="نیاز به سپرده">{toPersianDigits(detail.depositRequired || "اعلام نشده")}</DetailValue>
          <DetailValue label="مدت زمان خواب سپرده">{detail.depositHoldingMonths === null ? "اعلام نشده" : `${formatNumber(detail.depositHoldingMonths)} ماه`}</DetailValue>
        </DetailGroup>
        <DetailGroup>
          <DetailValue label="نوع ضمانت">{toPersianDigits(detail.guaranteeType || "اعلام نشده")}</DetailValue>
          <DetailValue label="حساب سپرده لازم">{toPersianDigits(detail.requiredDepositAccount || "اعلام نشده")}</DetailValue>
        </DetailGroup>
      </div>
    </article>
    <h2>شرایط و مدارک مورد نیاز</h2>
    <section className="hp-loan-details-conditions">
      {detail.conditions.length ? <ul>{detail.conditions.map((condition, index) => <li key={`${index}-${condition}`}>{toPersianDigits(condition)}</li>)}</ul> : <p>شرط یا مدرک تأییدشده‌ای برای نمایش ثبت نشده است.</p>}
    </section>
    <div className="hp-loan-details-analysis-bar">
      <button type="button" onClick={() => onAiAnalysis?.(detail.loanId)}>تحلیل با هوش مصنوعی</button>
    </div>
  </>;
}
