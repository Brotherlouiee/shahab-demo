import { useEffect, useState } from "react";

import { fetchLoanDetails } from "../../loan-details/loanDetailsApi.js";

function formatPercent(value) {
  if (typeof value !== "number") return "نامشخص";
  return `${Math.round(value * 100).toLocaleString("fa-IR").replaceAll("٬", "/")}٪`;
}

/**
 * Selection-only card for the restored comparison route. It consumes the
 * server-owned recommendation identity and score as display data; it never
 * fetches, ranks, or invents a loan fact.
 */
export default function LoanComparisonCard({
  recommendation,
  selected,
  onToggle,
}) {
  const [bankLogoReference, setBankLogoReference] = useState(null);
  useEffect(() => {
    const controller = new AbortController();
    fetchLoanDetails(recommendation.loanId, { signal: controller.signal })
      .then((detail) => setBankLogoReference(detail?.bankLogoReference ?? null))
      .catch(() => { if (!controller.signal.aborted) setBankLogoReference(null); });
    return () => controller.abort();
  }, [recommendation.loanId]);
  return (
    <article className="hp-loan-result-card is-compact hp-loan-compare-card">
      <div className="hp-loan-result-head">
        <button
          className={`hp-loan-compare-check ${selected ? "is-selected" : ""}`}
          type="button"
          onClick={onToggle}
          aria-label={`انتخاب ${recommendation.loanName}`}
          aria-pressed={selected}
        />
        <div>{bankLogoReference ? <img src={bankLogoReference} alt={recommendation.lenderName} referrerPolicy="no-referrer" /> : null}<span>«{recommendation.lenderName}»</span></div>
        <strong>{recommendation.loanName}</strong>
      </div>
      <p className="hp-loan-match">
        تطابق با وضعیت مشتری: <b>{formatPercent(recommendation.compatibilityScore)}</b>
      </p>
    </article>
  );
}
