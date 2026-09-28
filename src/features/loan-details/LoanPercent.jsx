function formatPersianNumber(value) {
  return Number(value).toLocaleString("fa-IR").replaceAll("٬", "/");
}

/** Keep the numeric value and its trailing percent sign in one LTR isolate. */
export default function LoanPercent({ value, fallback = "اعلام نشده" }) {
  if (value === null || value === undefined) return fallback;
  const formattedValue = formatPersianNumber(value);

  return (
    <bdi dir="ltr" className="hp-loan-percent" aria-label={`${formattedValue} درصد`}>
      <span className="hp-loan-percent-sign">٪</span>
      <span className="hp-loan-percent-value">{formattedValue}</span>
    </bdi>
  );
}
