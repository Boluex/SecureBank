/**
 * Tabular history of an account's deposits and withdrawals.
 */
import { formatCurrency, formatDateTime } from "../utils/formatters.js";
import styles from "./TransactionList.module.css";

/**
 * Render the transaction history, or an empty-state message.
 * @param {{transactions: object[], currency: string}} props
 */
function TransactionList({ transactions, currency }) {
  if (transactions.length === 0) {
    return <p className={styles.empty}>No transactions yet.</p>;
  }

  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Date</th>
          <th>Type</th>
          <th>Description</th>
          <th className={styles.amountColumn}>Amount</th>
        </tr>
      </thead>
      <tbody>
        {transactions.map((transaction) => {
          const isDeposit = transaction.type === "deposit";
          const amountClass = isDeposit ? styles.deposit : styles.withdrawal;
          const sign = isDeposit ? "+" : "−";
          return (
            <tr key={transaction.id}>
              <td>{formatDateTime(transaction.created_at)}</td>
              <td>
                <span className={`${styles.badge} ${amountClass}`}>{transaction.type}</span>
              </td>
              <td>{transaction.description || "—"}</td>
              <td className={`${styles.amountColumn} ${amountClass}`}>
                {sign}
                {formatCurrency(transaction.amount, currency)}
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export default TransactionList;
