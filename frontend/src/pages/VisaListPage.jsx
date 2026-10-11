import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import visaAPI from '../services/visa'
import Button from '../components/Button'
import Input from '../components/Input'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function VisaListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['visa_apps', { search, status, page }],
    queryFn: async () => {
      const response = await visaAPI.applications.list({
        search,
        status,
        page,
      })
      return response.data
    },
  })

  const apps = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1

  const columns = [
    { key: 'visa_app_id', label: 'ID' },
    { 
      key: 'candidate',
      label: 'Candidate',
      render: (val, row) => row.candidate?.full_name || '-'
    },
    { key: 'visa_type_name', label: 'Visa Type' },
    { key: 'submission_date', label: 'Submitted' },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <Badge variant="default">{val}</Badge>,
    },
    {
      key: 'days_pending',
      label: 'Pending',
      render: (val) => val ? `${val} days` : '-',
    },
    {
      key: 'is_expired',
      label: 'Validity',
      render: (val, row) => {
        if (row.is_expired) return <Badge variant="danger">Expired</Badge>
        return <Badge variant="success">Valid</Badge>
      },
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Visa Applications</h1>
            <Button onClick={() => navigate('/visa/new')}>
              + New Application
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
              placeholder="Candidate, visa ID..."
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
                <option value="NOT_STARTED">Not Started</option>
                <option value="PREPARING">Preparing</option>
                <option value="SUBMITTED">Submitted</option>
                <option value="PROCESSING">Processing</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={apps}
            loading={isLoading}
            onRowClick={(row) => navigate(`/visa/${row.id}`)}
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