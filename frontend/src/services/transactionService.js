import api from "./api";

export const getTransactions = () => {
  return api.get("/transactions");
};

export const getItemHistory = (itemId, params = {}) => {
  return api.get(`/transactions/items/${itemId}/history` , { params });
}

export const withdrawMaterial = (id, itemData) => {
  return api.post(`/transactions/items/${id}/withdraw`, itemData);
}