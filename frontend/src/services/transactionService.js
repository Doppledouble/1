import api from "./api";

export const getTransactions = () => {
  return api.get("/transactions");
};

export const getItemHistory = (id) => {
  return api.get(`/transactions/items/${id}/history`);
}

export const withdrawMaterial = (id, itemData) => {
  return api.post(`/transactions/items/${id}/withdraw`, itemData);
}