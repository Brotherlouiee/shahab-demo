function formatPersianNumber(value) {
  return Number(value).toLocaleString("fa-IR").replaceAll("٬", "/");
}

/** Keep the numeric value and its trailing percent sign in one LTR isolate. */
export default function LoanPercent({ value, fallback = "اعلام نشده" }) {
  if (value === null || value === undefined) return fallback;

  return (
    <bdi dir="ltr" className="hp-loan-percent">
      <span>{formatPersianNumber(value)}</span><span>٪</span>
    </bdi>
  );
}
