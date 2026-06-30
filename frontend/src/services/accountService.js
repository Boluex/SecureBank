/**
 * Bank account API calls.
 */
import apiClient from "./apiClient.js";

/**
 * Fetch every account owned by the authenticated user.
 * @returns {Promise<object[]>} A list of account records.
 */
export async function fetchAccounts() {
  const response = await apiClient.get("/accounts");
  return response.data;
}

/**
 * Fetch a single account by its identifier.
 * @param {number|string} accountId
 * @returns {Promise<object>} The account record.
 */
export async function fetchAccount(accountId) {
  const response = await apiClient.get(`/accounts/${accountId}`);
  return response.data;
}

/**
 * Open a new account.
 * @param {{currency: string, initial_deposit: string}} payload
 * @returns {Promise<object>} The created account record.
 */
export async function createAccount(payload) {
  const response = await apiClient.post("/accounts", payload);
  return response.data;
}

/**
 * Permanently close an empty account.
 * @param {number|string} accountId
 */
export async function deleteAccount(accountId) {
  await apiClient.delete(`/accounts/${accountId}`);
}
