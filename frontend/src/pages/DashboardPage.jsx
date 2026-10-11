import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import candidatesAPI from '../services/candidates'
import Button from '../components/Button'
import Badge from '../components/Badge'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  // Fetch candidates stats
  const { data: candidatesData } = useQuery({
    queryKey: ['candidates-stats'],
    queryFn: () => candidatesAPI.list({ page_size: 100 }).then((res) => res.data),
  })

  const candidates = candidatesData?.results || []
  
  // Calculate stats
  const stats = {
    total: candidatesData?.count || 0,
    available: candidates.filter((c) => c.current_status === 'AVAILABLE').length,
    applied: candidates.filter((c) => c.current_status === 'APPLIED').length,
    selected: candidates.filter((c) => c.current_status === 'SELECTED').length,
    deployed: candidates.filter((c) => c.current_status === 'DEPLOYED').length,
    expiring: candidates.filter((c) => c.passport_validity_days >= 0 && c.passport_validity_days <= 90).length,
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Top Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">SMART CAREER</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-700 text-sm">Welcome, {user?.email}</span>
            <Button variant="secondary" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </nav>

      {/* Sidebar + Main Content */}
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-gray-800 text-white min-h-screen p-4">
          <nav className="space-y-2">
            <NavLink icon="📊" label="Dashboard" active onClick={() => {}} />
            <NavLink
              icon="👥"
              label="Candidates"
              onClick={() => navigate('/candidates')}
            />
            <NavLink icon="💼" label="Jobs" onClick={() => {}} />
            <NavLink icon="📋" label="Applications" onClick={() => {}} />
            <NavLink icon="📄" label="Documents" onClick={() => {}} />
            <NavLink icon="🏥" label="Medical" onClick={() => {}} />
            <NavLink icon="✈️" label="Visa" onClick={() => {}} />
            <NavLink icon="💰" label="Finance" onClick={() => {}} />
            <NavLink icon="🤖" label="AI" onClick={() => {}} />
            <NavLink icon="🏥" label="Medical" onClick={() => navigate('/medical')} />
            <NavLink icon="✈️" label="Visa" onClick={() => navigate('/visa')} />
            <NavLink icon="🎫" label="Tickets" onClick={() => navigate('/tickets')} />
            <NavLink icon="🚀" label="Deployment" onClick={() => navigate('/deployment')} />
              
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-8">
          <div className="max-w-6xl">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h2>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
              <StatCard label="Total" value={stats.total} color="blue" />
              <StatCard label="Available" value={stats.available} color="green" />
              <StatCard label="Applied" value={stats.applied} color="purple" />
              <StatCard label="Selected" value={stats.selected} color="yellow" />
              <StatCard label="Deployed" value={stats.deployed} color="indigo" />
              <StatCard label="⚠️ Expiring" value={stats.expiring} color="red" />
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-8">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h3>
              <div className="flex gap-4 flex-wrap">
                <Button onClick={() => navigate('/candidates/new')}>+ New Candidate</Button>
                <Button variant="secondary" onClick={() => navigate('/candidates')}>
                  View All Candidates
                </Button>
                <Button variant="ghost">Create Job</Button>
              </div>
            </div>

            {/* Recent Candidates */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Recent Candidates</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left px-4 py-2 text-sm font-semibold">Name</th>
                      <th className="text-left px-4 py-2 text-sm font-semibold">Mobile</th>
                      <th className="text-left px-4 py-2 text-sm font-semibold">Status</th>
                      <th className="text-left px-4 py-2 text-sm font-semibold">Passport</th>
                      <th className="text-left px-4 py-2 text-sm font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {candidates.slice(0, 5).map((candidate) => (
                      <tr key={candidate.id} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {candidate.full_name}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {candidate.mobile}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Badge variant="default">{candidate.current_status}</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm">
                          {candidate.is_passport_expired ? (
                            <Badge variant="danger">Expired</Badge>
                          ) : (
                            <Badge variant="success">
                              {candidate.passport_validity_days} days
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate(`/candidates/${candidate.id}`)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

function NavLink({ icon, label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'text-gray-300 hover:bg-gray-700'
      }`}
    >
      <span className="mr-2">{icon}</span>
      {label}
    </button>
  )
}

function StatCard({ label, value, color }) {
  const colors = {
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    green: 'bg-green-50 border-green-200 text-green-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
  }

  return (
    <div className={`${colors[color]} border rounded-lg p-4 text-center`}>
      <p className="text-xs font-semibold uppercase">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  )
}