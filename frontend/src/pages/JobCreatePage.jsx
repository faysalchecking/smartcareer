import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import jobsAPI from '../services/jobs'
import Button from '../components/Button'
import Input from '../components/Input'

export default function JobCreatePage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    position: '',
    country: '',
    salary: '',
    currency: 'USD',
    requirements: '',
    benefits: '',
  })
  const [error, setError] = useState('')

  const createMutation = useMutation({
    mutationFn: (data) => jobsAPI.create(data),
    onSuccess: (response) => {
      navigate(`/jobs/${response.data.id}`)
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Error creating job')
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
    if (!formData.position || !formData.country) {
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
          <h1 className="text-2xl font-bold text-gray-900">Create New Job</h1>
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
              label="Position *"
              name="position"
              value={formData.position}
              onChange={handleChange}
              required
            />

            <Input
              label="Country *"
              name="country"
              value={formData.country}
              onChange={handleChange}
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Salary"
                type="number"
                name="salary"
                value={formData.salary}
                onChange={handleChange}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency
                </label>
                <select
                  name="currency"
                  value={formData.currency}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="USD">USD</option>
                  <option value="SAR">SAR</option>
                  <option value="AED">AED</option>
                  <option value="QAR">QAR</option>
                  <option value="BDT">BDT</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Requirements
              </label>
              <textarea
                name="requirements"
                value={formData.requirements}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Benefits
              </label>
              <textarea
                name="benefits"
                value={formData.benefits}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
              />
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                type="submit"
                disabled={createMutation.isPending}
              >
                {createMutation.isPending ? 'Creating...' : 'Create Job'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/jobs')}
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