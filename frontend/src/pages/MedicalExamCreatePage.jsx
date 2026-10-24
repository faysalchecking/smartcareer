import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import medicalAPI from '../services/medical'
import Button from '../components/Button'
import Input from '../components/Input'

export default function MedicalExamCreatePage() {
  const navigate = useNavigate()
  const { candidateId } = useParams()
  const [formData, setFormData] = useState({
    candidate: candidateId || '',
    scheduled_date: '',
    exam_type: 'GENERAL',
  })
  const [error, setError] = useState('')

  const createMutation = useMutation({
    mutationFn: (data) => medicalAPI.create(data),
    onSuccess: () => {
      navigate('/medical')
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Error creating medical exam')
    },
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.candidate || !formData.scheduled_date) {
      setError('Please fill in all required fields')
      return
    }
    createMutation.mutate(formData)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Schedule Medical Exam</h1>
        </div>
      </div>

      {/* Form */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Candidate ID *"
              name="candidate"
              value={formData.candidate}
              onChange={handleChange}
              required
            />

            <Input
              label="Scheduled Date *"
              type="date"
              name="scheduled_date"
              value={formData.scheduled_date}
              onChange={handleChange}
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Exam Type
              </label>
              <select
                name="exam_type"
                value={formData.exam_type}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="GENERAL">General</option>
                <option value="COMPREHENSIVE">Comprehensive</option>
                <option value="FOLLOW_UP">Follow Up</option>
              </select>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                type="submit"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? 'Scheduling...' : 'Schedule Exam'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/medical')}
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}