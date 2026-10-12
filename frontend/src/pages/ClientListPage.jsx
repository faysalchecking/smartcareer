import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import clientsAPI from '../services/clients'
import Button from '../components/Button'
import Input from '../components/Input'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function ClientListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [country, setCountry] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['clients', { search, status, country, page }],
    queryFn: async () => {
      const response = await clientsAPI.list({
        search,
        status,
        country,
        page,
      })
      return response.data
    },
  })

  const clients = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1

  const columns = [
    { key: 'client_id', label: 'ID' },
    { key: 'company_name', label: 'Company' },
    { key: 'contact_person', label: 'Contact' },
    { key: 'email', label: 'Email' },
    { key: 'country', label: 'Country' },
    {
      key: 'status',
      label: 'Status',
      render: (val) => {
        const colors = {
          ACTIVE: 'success',
          INACTIVE: 'warning',
          BLOCKED: 'danger',
        }
        return <Badge variant={colors[val] || 'default'}>{val}</Badge>
      },
    },
    {
      key: 'outstanding_balance',
      label: 'Outstanding',
      render: (val) => {
        if (!val || val === 0) return <span className="text-gray-500">-</span>
        return <span className={val > 0 ? 'text-red-600 font-semibold' : 'text-green-600'}>
          {val > 0 ? `+${val}` : val}
        </span>
      },
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Clients / Employers</h1>
            <Button onClick={() => navigate('/clients/new')}>
              + New Client
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input
              label="Search"
              placeholder="Company, contact..."
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
                <option value="">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="INACTIVE">Inactive</option>
                <option value="BLOCKED">Blocked</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Country
              </label>
              <select
                value={country}
                onChange={(e) => {
                  setCountry(e.target.value)
                  setPage(1)
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Countries</option>
                <option value="Saudi Arabia">Saudi Arabia</option>
                <option value="UAE">UAE</option>
                <option value="Qatar">Qatar</option>
                <option value="Malaysia">Malaysia</option>
                <option value="Oman">Oman</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={clients}
            loading={isLoading}
            onRowClick={(row) => navigate(`/clients/${row.id}`)}
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