import bankLogoAssets from "../../../data/contracts/bank-logo-assets.v1.json";

/** Verified, URL-safe application assets; the original external URL stays in the serving record for provenance. */
const ASSETS_BY_LENDER = Object.freeze(bankLogoAssets.byLender);

export function bankLogoAssetUrlForLender(lenderName) {
  const asset = ASSETS_BY_LENDER[lenderName];
  return asset ? `/${asset.assetKey}` : null;
}
