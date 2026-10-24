import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useParams } from 'react-router-dom'
import aiAPI from '../services/ai'
import Button from '../components/Button'
import Input from '../components/Input'

export default function AIChatPage() {
  const { conversationId } = useParams()
  const [message, setMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [localMessages, setLocalMessages] = useState([])
  const [error, setError] = useState('')
  const messagesEndRef = useRef(null)

  const { data: conversation, refetch, isLoading: convLoading } = useQuery({
    queryKey: ['ai_conversation', conversationId],
    queryFn: () => aiAPI.getConversation(conversationId),
    enabled: !!conversationId,
  })

  const sendMessageMutation = useMutation({
    mutationFn: (msg) => aiAPI.sendMessage(conversationId, msg),
    onSuccess: (response) => {
      setMessage('')
      setError('')
      setLocalMessages([])
      refetch()
    },
    onError: (err) => {
      setError(
        err.response?.data?.error || 
        'Failed to send message. Make sure AI provider is configured.'
      )
      setIsLoading(false)
    },
  })

  const handleSendMessage = () => {
    if (!message.trim()) return
    
    setError('')
    setIsLoading(true)
    
    // Add to local messages immediately for UX
    setLocalMessages(prev => [...prev, { role: 'USER', content: message }])
    
    sendMessageMutation.mutate(message)
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [conversation?.data?.messages, localMessages])

  if (convLoading) {
    return <div className="text-center py-12">Loading conversation...</div>
  }

  if (!conversation) {
    return <div className="text-center py-12">Conversation not found</div>
  }

  const messages = conversation.data.messages || []

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <h1 className="text-xl font-bold text-gray-900">
          {conversation.data.title || 'SMART AI Chat'}
        </h1>
        <p className="text-sm text-gray-500">
          Messages: {conversation.data.total_messages}
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === 'USER' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-md px-4 py-2 rounded-lg ${
                msg.role === 'USER'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs mt-1 opacity-70">
                {new Date(msg.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}
        {localMessages.map((msg, idx) => (
          <div key={`local-${idx}`} className="flex justify-end">
            <div className="max-w-md px-4 py-2 rounded-lg bg-blue-400 text-white opacity-70">
              <p className="text-sm">{msg.content}</p>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border-t border-red-200 p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <Input
            placeholder="Ask SMART AI..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSendMessage()
              }
            }}
            disabled={isLoading}
          />
          <Button
            onClick={handleSendMessage}
            disabled={isLoading || !message.trim()}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </Button>
        </div>
      </div>
    </div>
  )
}