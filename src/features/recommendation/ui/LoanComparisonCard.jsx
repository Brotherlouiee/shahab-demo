import { bankLogoAssetUrlForLender } from "../../loan-details/bankLogoAssetUrl.mjs";
import LoanPercent from "../../loan-details/LoanPercent.jsx";

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
  const bankLogoReference = bankLogoAssetUrlForLender(recommendation.lenderName);
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
        تطابق با وضعیت مشتری: <b>{typeof recommendation.compatibilityScore === "number" ? <LoanPercent value={Math.round(recommendation.compatibilityScore * 100)} /> : "نامشخص"}</b>
      </p>
    </article>
  );
}
