import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import alertsAPI from '../services/alerts'
import Button from '../components/Button'
import Table from '../components/Table'
import Badge from '../components/Badge'

export default function AlertCenterPage() {
  const navigate = useNavigate()
  const [showActive, setShowActive] = useState(true)

  const { data: activeData, isLoading: activeLoading } = useQuery({
    queryKey: ['alerts_active'],
    queryFn: async () => {
      const response = await alertsAPI.active()
      return response.data
    },
    enabled: showActive,
  })

  const { data: statsData } = useQuery({
    queryKey: ['alerts_stats'],
    queryFn: async () => {
      const response = await alertsAPI.statistics()
      return response.data
    },
  })

  const alerts = activeData || []
  const stats = statsData || {}

  const getSeverityColor = (severity) => {
    const colors = {
      CRITICAL: 'danger',
      HIGH: 'warning',
      MEDIUM: 'default',
      LOW: 'info',
    }
    return colors[severity] || 'default'
  }

  const columns = [
    { key: 'alert_id', label: 'ID' },
    { key: 'title', label: 'Alert' },
    { 
      key: 'candidate_name',
      label: 'Candidate',
      render: (val) => val || '-'
    },
    {
      key: 'severity',
      label: 'Severity',
      render: (val) => <Badge variant={getSeverityColor(val)}>{val}</Badge>,
    },
    {
      key: 'alert_type',
      label: 'Type',
    },
    {
      key: 'is_acknowledged',
      label: 'Status',
      render: (val) => (
        <Badge variant={val ? 'success' : 'warning'}>
          {val ? 'Acknowledged' : 'Pending'}
        </Badge>
      ),
    },
    {
      key: 'alert_date',
      label: 'Date',
      render: (val) => new Date(val).toLocaleDateString(),
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Alert Center</h1>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="text-gray-500 text-sm">Total Active</div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.total_active || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-red-500">
            <div className="text-gray-500 text-sm">Critical</div>
            <div className="text-3xl font-bold text-red-600">
              {stats.critical || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-yellow-500">
            <div className="text-gray-500 text-sm">High</div>
            <div className="text-3xl font-bold text-yellow-600">
              {stats.high || 0}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
            <div className="text-gray-500 text-sm">Unacknowledged</div>
            <div className="text-3xl font-bold text-blue-600">
              {stats.unacknowledged || 0}
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={alerts}
            loading={activeLoading}
            onRowClick={(row) => navigate(`/alerts/${row.id}`)}
          />
        </div>

        {alerts.length === 0 && !activeLoading && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No active alerts</p>
          </div>
        )}
      </div>
    </div>
  )
}