import apiClient from './api'

export const financeAPI = {
  // Services
  services: () => apiClient.get('/finance/services/'),
  
  // Vendors
  vendors: (params = {}) => apiClient.get('/finance/vendors/', { params }),
  createVendor: (data) => apiClient.post('/finance/vendors/', data),
  
  // Purchases
  purchases: (params = {}) => apiClient.get('/finance/purchases/', { params }),
  createPurchase: (data) => apiClient.post('/finance/purchases/', data),
  updatePurchase: (id, data) => apiClient.patch(`/finance/purchases/${id}/`, data),
  markPurchaseReceived: (id) => apiClient.post(`/finance/purchases/${id}/mark_received/`),
  
  // Sales
  sales: (params = {}) => apiClient.get('/finance/sales/', { params }),
  createSale: (data) => apiClient.post('/finance/sales/', data),
  
  // Invoices
  invoices: (params = {}) => apiClient.get('/finance/invoices/', { params }),
  createInvoice: (data) => apiClient.post('/finance/invoices/', data),
  invoicesByClient: (clientId) => apiClient.get(`/finance/invoices/by_client/${clientId}/`),
  
  // Payments
  payments: (params = {}) => apiClient.get('/finance/payments/', { params }),
  createPayment: (data) => apiClient.post('/finance/payments/', data),
  
  // Expenses
  expenses: (params = {}) => apiClient.get('/finance/expenses/', { params }),
  createExpense: (data) => apiClient.post('/finance/expenses/', data),
  approveExpense: (id) => apiClient.post(`/finance/expenses/${id}/approve/`),
  
  // Commissions
  commissions: (params = {}) => apiClient.get('/finance/commissions/', { params }),
  commissionsByAgent: (agentId) => apiClient.get(`/finance/commissions/by_agent/${agentId}/`),
  
  // Tax
  taxes: () => apiClient.get('/finance/taxes/'),
  
  // Ledger
  ledger: (params = {}) => apiClient.get('/finance/ledger/', { params }),
  ledgerByReference: (refType, refId) => 
    apiClient.get('/finance/ledger/by_reference/', { params: { ref_type: refType, ref_id: refId } }),
  
  // Bank Accounts
  accounts: () => apiClient.get('/finance/accounts/'),
}

export default financeAPI