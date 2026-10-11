import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import medicalAPI from '../services/medical'
import Button from '../components/Button'
import Input from '../components/Input'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function MedicalListPage() {
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['medical_exams', { search, status, page }],
    queryFn: async () => {
      const response = await medicalAPI.list({
        search,
        status,
        page,
      })
      return response.data
    },
  })

  const exams = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1

  const columns = [
    { key: 'medical_exam_id', label: 'ID' },
    { 
      key: 'candidate',
      label: 'Candidate',
      render: (val, row) => row.candidate?.full_name || '-'
    },
    { key: 'exam_type', label: 'Type' },
    { key: 'scheduled_date', label: 'Date' },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <Badge variant="default">{val}</Badge>,
    },
    {
      key: 'result',
      label: 'Result',
      render: (val) => {
        if (!val) return '-'
        return <Badge variant={val === 'PASS' ? 'success' : 'danger'}>{val}</Badge>
      },
    },
    {
      key: 'days_until_expiry',
      label: 'Certificate',
      render: (val, row) => {
        if (row.is_expired) return <Badge variant="danger">Expired</Badge>
        if (!val) return '-'
        return <Badge variant={val <= 90 ? 'warning' : 'success'}>{val} days</Badge>
      },
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">Medical Exams</h1>
            <Button onClick={() => navigate('/medical/new')}>
              + Schedule Exam
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
              placeholder="Candidate, exam ID..."
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
                <option value="SCHEDULED">Scheduled</option>
                <option value="ATTENDED">Attended</option>
                <option value="PASSED">Passed</option>
                <option value="FAILED">Failed</option>
                <option value="EXPIRED">Expired</option>
              </select>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={exams}
            loading={isLoading}
            onRowClick={(row) => navigate(`/medical/${row.id}`)}
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