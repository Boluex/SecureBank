/**
 * Summary card for a single bank account on the dashboard.
 */
import { useNavigate } from "react-router-dom";
import { formatCurrency, maskAccountNumber } from "../utils/formatters.js";
import styles from "./AccountCard.module.css";

/**
 * Render a clickable account summary.
 * @param {{account: {id: number, account_number: string, currency: string, balance: string}}} props
 */
function AccountCard({ account }) {
  const navigate = useNavigate();

  return (
    <button
      className={styles.card}
      onClick={() => navigate(`/accounts/${account.id}`)}
      aria-label={`Open account ${maskAccountNumber(account.account_number)}`}
    >
      <span className={styles.currency}>{account.currency}</span>
      <span className={styles.number}>{maskAccountNumber(account.account_number)}</span>
      <span className={styles.balance}>
        {formatCurrency(account.balance, account.currency)}
      </span>
      <span className={styles.cta}>View transactions →</span>
    </button>
  );
}

export default AccountCard;
