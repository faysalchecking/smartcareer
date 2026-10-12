import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import financeAPI from '../services/finance'
import Button from '../components/Button'
import Input from '../components/Input'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function PurchaseListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['purchases', { search, status, page }],
    queryFn: async () => {
      const response = await financeAPI.purchases({
        search,
        status,
        page,
      })
      return response.data
    },
  })

  const purchases = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1

  const columns = [
    { key: 'purchase_id', label: 'ID' },
    { key: 'vendor_name', label: 'Vendor' },
    { key: 'service_name', label: 'Service' },
    { key: 'purchase_date', label: 'Date' },
    {
      key: 'total_cost',
      label: 'Cost',
      render: (val, row) => `${row.currency} ${val}`,
    },
    {
      key: 'paid_amount',
      label: 'Paid',
      render: (val, row) => `${row.currency} ${val}`,
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => {
        const colors = {
          DRAFT: 'secondary',
          ORDERED: 'info',
          RECEIVED: 'success',
          PAID: 'success',
          PARTIALLY_PAID: 'warning',
          CANCELLED: 'danger',
        }
        return <Badge variant={colors[val] || 'default'}>{val}</Badge>
      },
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Purchases</h1>
            <Button onClick={() => navigate('/finance/purchases/new')}>
              + New Purchase
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input
              label="Search"
              placeholder="Vendor, purchase ID..."
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => {
                  setStatus(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                <option value="DRAFT">Draft</option>
                <option value="ORDERED">Ordered</option>
                <option value="RECEIVED">Received</option>
                <option value="PAID">Paid</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={purchases}
            loading={isLoading}
            onRowClick={(row) => navigate(`/finance/purchases/${row.id}`)}
          />
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex justify-center gap-2">
            <Button
              variant="secondary"
              disabled={page === 1}
              onClick={() => setPage(page - 1)}
            >
              Previous
            </Button>
            <span className="px-4 py-2 text-gray-700">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="secondary"
              disabled={page === totalPages}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}