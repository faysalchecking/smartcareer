import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import applicationsAPI from '../services/applications'
import Button from '../components/Button'
import Badge from '../components/Badge'

export default function ApplicationDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [rejectReason, setRejectReason] = useState('')
  const [shortlistReason, setShortlistReason] = useState('')
  const [showRejectModal, setShowRejectModal] = useState(false)
  const [showShortlistModal, setShowShortlistModal] = useState(false)

  const { data: application, isLoading, refetch } = useQuery({
    queryKey: ['application', id],
    queryFn: () => applicationsAPI.get(id).then((res) => res.data),
  })

  const shortlistMutation = useMutation({
    mutationFn: () => applicationsAPI.shortlist(id, shortlistReason),
    onSuccess: () => {
      refetch()
      setShowShortlistModal(false)
      setShortlistReason('')
    },
  })

  const rejectMutation = useMutation({
    mutationFn: () => applicationsAPI.reject(id, rejectReason),
    onSuccess: () => {
      refetch()
      setShowRejectModal(false)
      setRejectReason('')
    },
  })

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!application) {
    return <div className="min-h-screen flex items-center justify-center">Application not found</div>
  }

  const screening = application.screening_result

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {application.candidate.full_name}
              </h1>
              <p className="text-gray-600 mt-1">{application.job.title}</p>
              <p className="text-gray-600 text-sm">{application.application_id}</p>
            </div>
            <div className="flex gap-2">
              {application.status === 'SCREENING' && (
                <>
                  <Button
                    onClick={() => setShowShortlistModal(true)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    Shortlist
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => setShowRejectModal(true)}
                  >
                    Reject
                  </Button>
                </>
              )}
              <Button variant="ghost" onClick={() => navigate('/applications')}>
                Back
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Quick Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Status</p>
            <Badge className="mt-2">{application.status}</Badge>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Score</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {application.screening_score?.toFixed(1) || 0}%
            </p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <p className="text-sm text-gray-600">Eligibility</p>
            {application.is_eligible_by_criteria ? (
              <Badge variant="success" className="mt-2">
                Eligible
              </Badge>
            ) : (
              <Badge variant="danger" className="mt-2">
                Not Eligible
              </Badge>
            )}
          </div>
        </div>

        {/* Screening Result */}
        {screening && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Screening Result</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600">Result</p>
                <Badge className="mt-2">{screening.result}</Badge>
              </div>
              <div>
                <p className="text-sm text-gray-600">Score</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {screening.total_score?.toFixed(1)}%
                </p>
              </div>
              <div className="md:col-span-2">
                <p className="text-sm text-gray-600">Reasoning</p>
                <p className="text-gray-900 mt-1">{screening.reasoning}</p>
              </div>
            </div>
          </div>
        )}

        {/* Candidate Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Candidate Info</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Age</p>
                <p className="text-gray-900">{application.candidate.age} years</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Experience</p>
                <p className="text-gray-900">{application.candidate.experience || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Education</p>
                <p className="text-gray-900">{application.candidate.education || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Languages</p>
                <p className="text-gray-900">{application.candidate.languages || '-'}</p>
              </div>
            </div>
          </div>

          {/* Job Info */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Job Info</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Country</p>
                <p className="text-gray-900">{application.job.country}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Salary</p>
                <p className="text-gray-900">
                  {application.job.currency} {application.job.salary_max || 'TBD'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Experience Required</p>
                <p className="text-gray-900">{application.job.experience_years || '-'} years</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Positions Available</p>
                <p className="text-gray-900">{application.job.available_positions}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showShortlistModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Shortlist Candidate</h2>
            <textarea
              placeholder="Reason for shortlisting..."
              value={shortlistReason}
              onChange={(e) => setShortlistReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
              rows="4"
            />
            <div className="flex gap-2">
              <Button
                onClick={() => shortlistMutation.mutate()}
                loading={shortlistMutation.isPending}
                className="flex-1"
              >
                Shortlist
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowShortlistModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}

      {showRejectModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">Reject Application</h2>
            <textarea
              placeholder="Reason for rejection..."
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg mb-4"
              rows="4"
            />
            <div className="flex gap-2">
              <Button
                variant="danger"
                onClick={() => rejectMutation.mutate()}
                loading={rejectMutation.isPending}
                className="flex-1"
              >
                Reject
              </Button>
              <Button
                variant="secondary"
                onClick={() => setShowRejectModal(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}