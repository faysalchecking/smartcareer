import { useQuery } from '@tanstack/react-query'
import financeAPI from '../services/finance'
import { useNavigate } from 'react-router-dom'
import Button from '../components/Button'

export default function FinanceDashboardPage() {
  const navigate = useNavigate()

  const { data: invoicesData } = useQuery({
    queryKey: ['finance_invoices_summary'],
    queryFn: async () => {
      const response = await financeAPI.invoices({ page: 1 })
      return response.data
    },
  })

  const { data: purchasesData } = useQuery({
    queryKey: ['finance_purchases_summary'],
    queryFn: async () => {
      const response = await financeAPI.purchases({ page: 1 })
      return response.data
    },
  })

  const invoices = invoicesData?.results || []
  const purchases = purchasesData?.results || []

  const totalRevenue = invoices.reduce((sum, inv) => sum + parseFloat(inv.total || 0), 0)
  const totalOutstanding = invoices.reduce((sum, inv) => sum + parseFloat(inv.outstanding || 0), 0)
  const totalPurchaseCost = purchases.reduce((sum, pur) => sum + parseFloat(pur.total_cost || 0), 0)

  const stats = [
    {
      label: 'Total Revenue',
      value: totalRevenue.toFixed(2),
      color: 'green',
    },
    {
      label: 'Outstanding',
      value: totalOutstanding.toFixed(2),
      color: 'red',
    },
    {
      label: 'Total Purchases',
      value: totalPurchaseCost.toFixed(2),
      color: 'blue',
    },
    {
      label: 'Gross Margin',
      value: (totalRevenue - totalPurchaseCost).toFixed(2),
      color: 'purple',
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Finance Dashboard</h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, idx) => (
            <div
              key={idx}
              className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${
                stat.color === 'green' ? 'border-green-500' :
                stat.color === 'red' ? 'border-red-500' :
                stat.color === 'blue' ? 'border-blue-500' :
                'border-purple-500'
              }`}
            >
              <div className="text-gray-500 text-sm">{stat.label}</div>
              <div className={`text-3xl font-bold mt-2 ${
                stat.color === 'green' ? 'text-green-600' :
                stat.color === 'red' ? 'text-red-600' :
                stat.color === 'blue' ? 'text-blue-600' :
                'text-purple-600'
              }`}>
                {stat.value}
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button onClick={() => navigate('/finance/invoices')}>
              View Invoices
            </Button>
            <Button onClick={() => navigate('/finance/purchases')}>
              View Purchases
            </Button>
            <Button onClick={() => navigate('/finance/payments')}>
              Record Payment
            </Button>
          </div>
        </div>

        {/* Recent Invoices */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Invoices</h2>
          {invoices.length === 0 ? (
            <p className="text-gray-500">No invoices</p>
          ) : (
            <div className="space-y-3">
              {invoices.slice(0, 5).map((inv) => (
                <div
                  key={inv.id}
                  className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer"
                  onClick={() => navigate(`/finance/invoices/${inv.id}`)}
                >
                  <div>
                    <div className="font-semibold">{inv.invoice_id}</div>
                    <div className="text-sm text-gray-500">{inv.client_name}</div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">{inv.total}</div>
                    <div className={inv.outstanding > 0 ? 'text-red-600 text-sm' : 'text-green-600 text-sm'}>
                      {inv.outstanding > 0 ? `Outstanding: ${inv.outstanding}` : 'Paid'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}