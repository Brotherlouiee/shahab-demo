import BankIdentity from "../../loan-details/BankIdentity.jsx";
import LoanPercent from "../../loan-details/LoanPercent.jsx";
import { toPersianDigits } from "../../loan-details/toPersianDigits.mjs";
import { compatibilityBandForScore } from "./compatibilityDisplay.mjs";

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
  const compatibilityBand = compatibilityBandForScore(recommendation.compatibilityScore);

  return (
    <article className="hp-loan-result-card is-compact hp-loan-compare-card" data-compatibility-band={compatibilityBand || undefined}>
      <button
        className={`hp-loan-compare-check ${selected ? "is-selected" : ""}`}
        type="button"
        onClick={onToggle}
        aria-label={`انتخاب ${toPersianDigits(recommendation.loanName)}`}
        aria-pressed={selected}
      />
      <div className="hp-loan-result-head">
        <BankIdentity lenderName={recommendation.lenderName} />
        <strong title={toPersianDigits(recommendation.loanName)} aria-label={toPersianDigits(recommendation.loanName)}>{toPersianDigits(recommendation.loanName)}</strong>
      </div>
      <p className="hp-loan-match">
        تطابق با وضعیت مشتری: <b>{typeof recommendation.compatibilityScore === "number" ? <LoanPercent value={Math.round(recommendation.compatibilityScore * 100)} /> : "نامشخص"}</b>
      </p>
    </article>
  );
}
