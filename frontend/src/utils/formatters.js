/**
 * Presentation helpers for money and dates.
 *
 * Pure functions with no side effects so they are trivial to reason about and
 * reuse across components.
 */

/**
 * Format a numeric amount as a localized currency string.
 * @param {number|string} amount - The raw amount (e.g. "125.00").
 * @param {string} [currency="USD"] - ISO 4217 currency code.
 * @returns {string} A formatted currency string such as "$125.00".
 */
export function formatCurrency(amount, currency = "USD") {
  const numericAmount = Number(amount);
  if (Number.isNaN(numericAmount)) {
    return String(amount);
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
  }).format(numericAmount);
}

/**
 * Format an ISO timestamp as a human-readable date and time.
 * @param {string} isoTimestamp - An ISO 8601 timestamp.
 * @returns {string} A localized date-time string.
 */
export function formatDateTime(isoTimestamp) {
  const parsedDate = new Date(isoTimestamp);
  if (Number.isNaN(parsedDate.getTime())) {
    return isoTimestamp;
  }
  return parsedDate.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/**
 * Mask all but the last four digits of an account number.
 * @param {string} accountNumber - The full account number.
 * @returns {string} A masked representation such as "•••• 1234".
 */
export function maskAccountNumber(accountNumber) {
  if (!accountNumber || accountNumber.length < 4) {
    return accountNumber ?? "";
  }
  return `•••• ${accountNumber.slice(-4)}`;
}
