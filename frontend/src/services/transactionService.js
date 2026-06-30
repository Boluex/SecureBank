/**
 * Transaction API calls: deposits, withdrawals and history.
 */
import apiClient from "./apiClient.js";

/**
 * Deposit money into an account.
 * @param {number|string} accountId
 * @param {{amount: string, description: string}} payload
 * @returns {Promise<object>} The recorded transaction.
 */
export async function deposit(accountId, payload) {
  const response = await apiClient.post(`/accounts/${accountId}/deposit`, payload);
  return response.data;
}

/**
 * Withdraw money from an account.
 * @param {number|string} accountId
 * @param {{amount: string, description: string}} payload
 * @returns {Promise<object>} The recorded transaction.
 */
export async function withdraw(accountId, payload) {
  const response = await apiClient.post(`/accounts/${accountId}/withdraw`, payload);
  return response.data;
}

/**
 * Fetch the transaction history for an account, newest first.
 * @param {number|string} accountId
 * @returns {Promise<object[]>} A list of transactions.
 */
export async function fetchTransactions(accountId) {
  const response = await apiClient.get(`/accounts/${accountId}/transactions`);
  return response.data;
}
