import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import aiAPI from '../services/ai'
import Button from '../components/Button'
import Table from '../components/Table'

export default function AIConversationsPage() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['ai_conversations', page],
    queryFn: () => aiAPI.conversations({ page }),
  })

  const conversations = data?.data?.results || []
  const totalPages = data?.data?.count ? Math.ceil(data.data.count / 20) : 1

  const createNewConversation = async () => {
    const response = await aiAPI.createConversation({
      title: `Chat - ${new Date().toLocaleString()}`,
    })
    navigate(`/ai/chat/${response.data.id}`)
  }

  const columns = [
    { key: 'conversation_id', label: 'ID' },
    { key: 'title', label: 'Title' },
    {
      key: 'total_messages',
      label: 'Messages',
    },
    {
      key: 'total_tokens_used',
      label: 'Tokens Used',
    },
    {
      key: 'created_at',
      label: 'Created',
      render: (val) => new Date(val).toLocaleDateString(),
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-900">SMART AI Chat</h1>
            <Button onClick={createNewConversation}>
              + New Conversation
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Table */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <Table
            columns={columns}
            data={conversations}
            loading={isLoading}
            onRowClick={(row) => navigate(`/ai/chat/${row.id}`)}
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