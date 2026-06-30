/**
 * Dashboard page listing the user's accounts and offering account creation.
 *
 * Demonstrates the standard async lifecycle used throughout the app: a loading
 * spinner, an inline error state with retry, and an empty state.
 */
import { useCallback, useEffect, useState } from "react";

import AccountCard from "../components/AccountCard.jsx";
import FormField from "../components/FormField.jsx";
import Navbar from "../components/Navbar.jsx";
import Spinner from "../components/Spinner.jsx";
import { createAccount, fetchAccounts } from "../services/accountService.js";
import { extractErrorMessage, validateAmount } from "../utils/validators.js";
import styles from "./Dashboard.module.css";

/** Render the accounts dashboard. */
function DashboardPage() {
  const [accounts, setAccounts] = useState([]);
  const [status, setStatus] = useState("loading");
  const [loadError, setLoadError] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [currency, setCurrency] = useState("USD");
  const [initialDeposit, setInitialDeposit] = useState("0");
  const [panelError, setPanelError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const loadAccounts = useCallback(async () => {
    setStatus("loading");
    setLoadError(null);
    try {
      setAccounts(await fetchAccounts());
      setStatus("ready");
    } catch (error) {
      setLoadError(extractErrorMessage(error, "Could not load your accounts."));
      setStatus("error");
    }
  }, []);

  useEffect(() => {
    loadAccounts();
  }, [loadAccounts]);

  const handleCreate = async (event) => {
    event.preventDefault();
    setPanelError(null);
    const depositError = initialDeposit === "0" ? null : validateAmount(initialDeposit);
    if (depositError) {
      setPanelError(depositError);
      return;
    }

    setIsSaving(true);
    try {
      const account = await createAccount({
        currency: currency.toUpperCase(),
        initial_deposit: initialDeposit || "0",
      });
      setAccounts((current) => [account, ...current]);
      setIsPanelOpen(false);
      setInitialDeposit("0");
      setCurrency("USD");
    } catch (error) {
      setPanelError(extractErrorMessage(error, "Could not open the account."));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className={styles.layout}>
      <Navbar />
      <div className={styles.container}>
        <div className={styles.header}>
          <h1>Your accounts</h1>
          <button className={styles.newButton} onClick={() => setIsPanelOpen((open) => !open)}>
            {isPanelOpen ? "Close" : "+ New account"}
          </button>
        </div>

        {isPanelOpen ? (
          <form className={styles.panel} onSubmit={handleCreate}>
            <h2>Open a new account</h2>
            {panelError ? <div className={styles.formError}>{panelError}</div> : null}
            <div className={styles.panelRow}>
              <FormField
                id="currency"
                label="Currency (ISO code)"
                value={currency}
                onChange={(event) => setCurrency(event.target.value)}
                placeholder="USD"
              />
              <FormField
                id="initial_deposit"
                label="Initial deposit"
                type="number"
                step="0.01"
                min="0"
                value={initialDeposit}
                onChange={(event) => setInitialDeposit(event.target.value)}
              />
            </div>
            <div className={styles.actions}>
              <button className={styles.newButton} type="submit" disabled={isSaving}>
                {isSaving ? "Opening…" : "Open account"}
              </button>
            </div>
          </form>
        ) : null}

        {status === "loading" ? <Spinner label="Loading accounts…" /> : null}

        {status === "error" ? (
          <div className={styles.empty}>
            <p>{loadError}</p>
            <button className={styles.secondary} onClick={loadAccounts}>
              Retry
            </button>
          </div>
        ) : null}

        {status === "ready" && accounts.length === 0 ? (
          <div className={styles.empty}>
            You have no accounts yet. Open one to get started.
          </div>
        ) : null}

        {status === "ready" && accounts.length > 0 ? (
          <div className={styles.grid}>
            {accounts.map((account) => (
              <AccountCard key={account.id} account={account} />
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default DashboardPage;
