import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import CandidateListPage from './pages/CandidateListPage'
import CandidateDetailPage from './pages/CandidateDetailPage'
import JobListPage from './pages/JobListPage'
import JobDetailPage from './pages/JobDetailPage'
import ApplicationListPage from './pages/ApplicationListPage'
import ApplicationDetailPage from './pages/ApplicationDetailPage'
import MedicalListPage from './pages/MedicalListPage'
import VisaListPage from './pages/VisaListPage'
import TicketListPage from './pages/TicketListPage'
import DeploymentListPage from './pages/DeploymentListPage'
import TaskListPage from './pages/TaskListPage'
import AlertCenterPage from './pages/AlertCenterPage'
import NotificationsPage from './pages/NotificationsPage'
import AgentListPage from './pages/AgentListPage'
import ClientListPage from './pages/ClientListPage'
import PurchaseListPage from './pages/PurchaseListPage'
import InvoiceListPage from './pages/InvoiceListPage'
import FinanceDashboardPage from './pages/FinanceDashboardPage'

const queryClient = new QueryClient()

// Protected Route Component
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return isAuthenticated ? children : <Navigate to="/login" />
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/candidates"
        element={
          <ProtectedRoute>
            <CandidateListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/candidates/:id"
        element={
          <ProtectedRoute>
            <CandidateDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/jobs"
        element={
          <ProtectedRoute>
            <JobListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/jobs/:id"
        element={
          <ProtectedRoute>
            <JobDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/applications"
        element={
          <ProtectedRoute>
            <ApplicationListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/applications/:id"
        element={
          <ProtectedRoute>
            <ApplicationDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/medical"
        element={
          <ProtectedRoute>
            <MedicalListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/visa"
        element={
          <ProtectedRoute>
            <VisaListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tickets"
        element={
          <ProtectedRoute>
            <TicketListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/deployment"
        element={
          <ProtectedRoute>
            <DeploymentListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/tasks"
        element={
          <ProtectedRoute>
            <TaskListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/alerts"
        element={
          <ProtectedRoute>
            <AlertCenterPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/notifications"
        element={
          <ProtectedRoute>
            <NotificationsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agents"
        element={
          <ProtectedRoute>
            <AgentListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/clients"
        element={
          <ProtectedRoute>
            <ClientListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/finance"
        element={
          <ProtectedRoute>
            <FinanceDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/finance/purchases"
        element={
          <ProtectedRoute>
            <PurchaseListPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/finance/invoices"
        element={
          <ProtectedRoute>
            <InvoiceListPage />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} />} />
    </Routes>
  )
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  )
}