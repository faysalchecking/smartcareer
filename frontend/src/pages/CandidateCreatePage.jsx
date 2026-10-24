import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import candidatesAPI from '../services/candidates'
import Button from '../components/Button'
import Input from '../components/Input'

export default function CandidateCreatePage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    date_of_birth: '',
    nationality: '',
    passport_number: '',
    address: '',
  })
  const [error, setError] = useState('')

  const createMutation = useMutation({
    mutationFn: (data) => candidatesAPI.create(data),
    onSuccess: (response) => {
      navigate(`/candidates/${response.data.id}`)
    },
    onError: (err) => {
      setError(err.response?.data?.detail || 'Error creating candidate')
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
    if (!formData.full_name || !formData.email || !formData.phone) {
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
          <h1 className="text-2xl font-bold text-gray-900">Create New Candidate</h1>
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
              label="Full Name *"
              name="full_name"
              value={formData.full_name}
              onChange={handleChange}
              required
            />

            <Input
              label="Email *"
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
            />

            <Input
              label="Phone *"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              required
            />

            <Input
              label="Date of Birth"
              type="date"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleChange}
            />

            <Input
              label="Nationality"
              name="nationality"
              value={formData.nationality}
              onChange={handleChange}
            />

            <Input
              label="Passport Number"
              name="passport_number"
              value={formData.passport_number}
              onChange={handleChange}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <textarea
                name="address"
                value={formData.address}
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
                {createMutation.isPending ? 'Creating...' : 'Create Candidate'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => navigate('/candidates')}
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