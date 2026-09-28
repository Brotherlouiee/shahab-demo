import { bankLogoAssetUrlForLender } from "./bankLogoAssetUrl.mjs";

/**
 * Keep the approved bank logo in a fixed box. The lender label has its own
 * bounded area, so its length cannot move either the logo or the loan title.
 */
export default function BankIdentity({ lenderName }) {
  const logoUrl = bankLogoAssetUrlForLender(lenderName);

  return (
    <div className="hp-bank-identity">
      <span className="hp-bank-logo-box">
        {logoUrl ? <img src={logoUrl} alt={lenderName} referrerPolicy="no-referrer" /> : null}
      </span>
      <span className="hp-bank-name" title={lenderName} aria-label={lenderName}>«{lenderName}»</span>
    </div>
  );
}
