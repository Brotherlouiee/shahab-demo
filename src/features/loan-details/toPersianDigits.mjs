const ASCII_DIGITS = "0123456789";
const ARABIC_INDIC_DIGITS = "٠١٢٣٤٥٦٧٨٩";
const PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

/** Convert display text to Persian digits without altering canonical source data. */
export function toPersianDigits(value) {
  return String(value).replace(/[0-9٠-٩]/g, (digit) => {
    const asciiIndex = ASCII_DIGITS.indexOf(digit);
    return PERSIAN_DIGITS[asciiIndex >= 0 ? asciiIndex : ARABIC_INDIC_DIGITS.indexOf(digit)];
  });
}
