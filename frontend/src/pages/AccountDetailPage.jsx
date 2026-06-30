/**
 * Account detail page: balance, deposits, withdrawals and history.
 *
 * Account and transaction data are loaded together. After any money movement
 * both are refetched so the displayed balance and ledger stay consistent with
 * the encrypted server-side state.
 */
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import Navbar from "../components/Navbar.jsx";
import Spinner from "../components/Spinner.jsx";
import TransactionForm from "../components/TransactionForm.jsx";
import TransactionList from "../components/TransactionList.jsx";
import { deleteAccount, fetchAccount } from "../services/accountService.js";
import { deposit, fetchTransactions, withdraw } from "../services/transactionService.js";
import { formatCurrency } from "../utils/formatters.js";
import { extractErrorMessage } from "../utils/validators.js";
import styles from "./AccountDetail.module.css";

/** Render the detail view for a single account. */
function AccountDetailPage() {
  const { accountId } = useParams();
  const navigate = useNavigate();
  const [account, setAccount] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [status, setStatus] = useState("loading");
  const [loadError, setLoadError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadData = useCallback(async () => {
    setStatus("loading");
    setLoadError(null);
    try {
      const [accountData, transactionData] = await Promise.all([
        fetchAccount(accountId),
        fetchTransactions(accountId),
      ]);
      setAccount(accountData);
      setTransactions(transactionData);
      setStatus("ready");
    } catch (error) {
      setLoadError(extractErrorMessage(error, "Could not load this account."));
      setStatus("error");
    }
  }, [accountId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleDeposit = async (payload) => {
    setActionError(null);
    await deposit(accountId, payload);
    await loadData();
  };

  const handleWithdraw = async (payload) => {
    setActionError(null);
    await withdraw(accountId, payload);
    await loadData();
  };

  const handleDelete = async () => {
    setActionError(null);
    setIsDeleting(true);
    try {
      await deleteAccount(accountId);
      navigate("/", { replace: true });
    } catch (error) {
      setActionError(extractErrorMessage(error, "Could not close this account."));
      setIsDeleting(false);
    }
  };

  return (
    <div className={styles.layout}>
      <Navbar />
      <div className={styles.container}>
        <button className={styles.back} onClick={() => navigate("/")}>
          ← Back to accounts
        </button>

        {status === "loading" ? <Spinner label="Loading account…" /> : null}

        {status === "error" ? (
          <div className={styles.error}>
            {loadError}{" "}
            <button className={styles.back} onClick={loadData}>
              Retry
            </button>
          </div>
        ) : null}

        {status === "ready" && account ? (
          <>
            <div className={styles.summary}>
              <div>
                <div className={styles.accountNumber}>
                  Account {account.account_number} · {account.currency}
                </div>
                <div className={styles.balance}>
                  {formatCurrency(account.balance, account.currency)}
                </div>
              </div>
              <button
                className={styles.deleteButton}
                onClick={handleDelete}
                disabled={isDeleting}
              >
                {isDeleting ? "Closing…" : "Close account"}
              </button>
            </div>

            {actionError ? <div className={styles.error}>{actionError}</div> : null}

            <div className={styles.forms}>
              <TransactionForm
                title="Deposit"
                actionLabel="Deposit"
                onSubmit={handleDeposit}
              />
              <TransactionForm
                title="Withdraw"
                actionLabel="Withdraw"
                onSubmit={handleWithdraw}
              />
            </div>

            <div className={styles.history}>
              <h2>Transaction history</h2>
              <TransactionList transactions={transactions} currency={account.currency} />
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default AccountDetailPage;
