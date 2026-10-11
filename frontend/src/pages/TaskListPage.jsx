import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import tasksAPI from '../services/tasks'
import Button from '../components/Button'
import Input from '../components/Input'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function TaskListPage() {
  const navigate = useNavigate()
  const [filter, setFilter] = useState('all')
  const [priority, setPriority] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['tasks', { filter, priority, page }],
    queryFn: async () => {
      let response
      if (filter === 'today') {
        response = await tasksAPI.today()
        return { results: response.data, count: response.data.length }
      } else if (filter === 'overdue') {
        response = await tasksAPI.overdue()
        return { results: response.data, count: response.data.length }
      } else {
        response = await tasksAPI.myTasks({
          status: filter === 'all' ? '' : filter,
          priority,
          page,
        })
        return response.data
      }
    },
  })

  const tasks = data?.results || []
  const totalPages = data?.count ? Math.ceil(data.count / 20) : 1

  const getPriorityColor = (priority) => {
    const colors = {
      CRITICAL: 'danger',
      HIGH: 'warning',
      MEDIUM: 'default',
      LOW: 'info',
    }
    return colors[priority] || 'default'
  }

  const getStatusColor = (status) => {
    const colors = {
      PENDING: 'warning',
      IN_PROGRESS: 'info',
      COMPLETED: 'success',
      OVERDUE: 'danger',
      CANCELLED: 'secondary',
    }
    return colors[status] || 'default'
  }

  const columns = [
    { key: 'task_id', label: 'ID' },
    { key: 'title', label: 'Title' },
    { 
      key: 'candidate_name',
      label: 'Candidate',
      render: (val) => val || '-'
    },
    { key: 'module', label: 'Module' },
    {
      key: 'priority',
      label: 'Priority',
      render: (val) => <Badge variant={getPriorityColor(val)}>{val}</Badge>,
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <Badge variant={getStatusColor(val)}>{val}</Badge>,
    },
    {
      key: 'due_date',
      label: 'Due',
      render: (val) => new Date(val).toLocaleDateString(),
    },
    {
      key: 'days_until_due',
      label: 'Days',
      render: (val) => {
        if (val === null) return '-'
        if (val < 0) return <Badge variant="danger">{Math.abs(val)} late</Badge>
        return <Badge variant={val <= 3 ? 'warning' : 'success'}>{val} days</Badge>
      },
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick filters */}
        <div className="flex gap-2 mb-6">
          <Button
            variant={filter === 'all' ? 'primary' : 'secondary'}
            onClick={() => {
              setFilter('all')
              setPage(1)
            }}
          >
            All
          </Button>
          <Button
            variant={filter === 'today' ? 'primary' : 'secondary'}
            onClick={() => setFilter('today')}
          >
            Today
          </Button>
          <Button
            variant={filter === 'PENDING' ? 'primary' : 'secondary'}
            onClick={() => {
              setFilter('PENDING')
              setPage(1)
            }}
          >
            Pending
          </Button>
          <Button
            variant={filter === 'overdue' ? 'primary' : 'secondary'}
            onClick={() => setFilter('overdue')}
          >
            Overdue
          </Button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              value={priority}
              onChange={(e) => {
                setPriority(e.target.value)
                setPage(1)
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Priorities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={tasks}
            loading={isLoading}
            onRowClick={(row) => navigate(`/tasks/${row.id}`)}
          />
        </div>

        {/* Pagination */}
        {totalPages > 1 && filter === 'all' && (
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