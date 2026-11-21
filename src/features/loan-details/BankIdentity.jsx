import { bankLogoAssetUrlForLender } from "./bankLogoAssetUrl.mjs";
import { toPersianDigits } from "./toPersianDigits.mjs";

/**
 * Keep the approved bank logo in a fixed box. The lender label has its own
 * bounded area, so its length cannot move either the logo or the loan title.
 */
export default function BankIdentity({ lenderName }) {
  const logoUrl = bankLogoAssetUrlForLender(lenderName);
  const displayLenderName = toPersianDigits(lenderName);

  return (
    <div className="hp-bank-identity">
      <span className="hp-bank-logo-box">
        {logoUrl ? <img src={logoUrl} alt={displayLenderName} referrerPolicy="no-referrer" /> : null}
      </span>
      <span className="hp-bank-name" title={displayLenderName} aria-label={displayLenderName}>«{displayLenderName}»</span>
    </div>
  );
}
