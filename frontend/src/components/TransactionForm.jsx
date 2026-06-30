/**
 * Inline form for depositing to or withdrawing from an account.
 */
import { useState } from "react";

import FormField from "./FormField.jsx";
import { extractErrorMessage, validateAmount } from "../utils/validators.js";
import styles from "./TransactionForm.module.css";

/**
 * Render a money-movement form.
 * @param {{
 *   title: string,
 *   actionLabel: string,
 *   onSubmit: (payload: {amount: string, description: string}) => Promise<void>,
 * }} props
 */
function TransactionForm({ title, actionLabel, onSubmit }) {
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const amountError = validateAmount(amount);
    if (amountError) {
      setError(amountError);
      return;
    }
    setError(null);
    setIsSubmitting(true);
    try {
      await onSubmit({ amount, description });
      setAmount("");
      setDescription("");
    } catch (submitError) {
      setError(extractErrorMessage(submitError, "The transaction failed."));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className={styles.form} onSubmit={handleSubmit}>
      <h3>{title}</h3>
      {error ? <div className={styles.error}>{error}</div> : null}
      <FormField
        id={`${actionLabel}-amount`}
        label="Amount"
        type="number"
        step="0.01"
        min="0"
        value={amount}
        onChange={(event) => setAmount(event.target.value)}
        placeholder="0.00"
      />
      <FormField
        id={`${actionLabel}-description`}
        label="Description (optional)"
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        placeholder="e.g. Paycheck"
      />
      <button className={styles.button} type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Processing…" : actionLabel}
      </button>
    </form>
  );
}

export default TransactionForm;
