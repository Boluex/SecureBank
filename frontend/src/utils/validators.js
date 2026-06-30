/**
 * Client-side input validation.
 *
 * Mirrors the backend's password policy and amount rules to give users fast
 * feedback. The backend remains the authoritative validator — these checks are
 * purely a UX convenience and never a security boundary.
 */

const MIN_PASSWORD_LENGTH = 10;
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validate an email address shape.
 * @param {string} email
 * @returns {string|null} An error message, or null when valid.
 */
export function validateEmail(email) {
  if (!email) {
    return "Email is required.";
  }
  if (!EMAIL_PATTERN.test(email)) {
    return "Enter a valid email address.";
  }
  return null;
}

/**
 * Validate a password against the strength policy.
 * @param {string} password
 * @returns {string|null} An error message, or null when valid.
 */
export function validatePassword(password) {
  if (password.length < MIN_PASSWORD_LENGTH) {
    return `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
  }
  if (!/[A-Z]/.test(password)) {
    return "Password must contain an uppercase letter.";
  }
  if (!/[a-z]/.test(password)) {
    return "Password must contain a lowercase letter.";
  }
  if (!/[0-9]/.test(password)) {
    return "Password must contain a digit.";
  }
  if (!/[^A-Za-z0-9]/.test(password)) {
    return "Password must contain a special character.";
  }
  return null;
}

/**
 * Validate a positive monetary amount.
 * @param {string} amount - The raw input value.
 * @returns {string|null} An error message, or null when valid.
 */
export function validateAmount(amount) {
  const numericAmount = Number(amount);
  if (!amount || Number.isNaN(numericAmount)) {
    return "Enter a valid amount.";
  }
  if (numericAmount <= 0) {
    return "Amount must be greater than zero.";
  }
  return null;
}

/**
 * Extract a human-readable message from an Axios error.
 * @param {unknown} error - The thrown error.
 * @param {string} fallback - Message used when none can be derived.
 * @returns {string} A displayable error message.
 */
export function extractErrorMessage(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0 && detail[0]?.msg) {
    return detail[0].msg;
  }
  return fallback;
}
