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
  const messagesEndRef = useRef(null)

  const { data: conversation, refetch } = useQuery({
    queryKey: ['ai_conversation', conversationId],
    queryFn: () => aiAPI.getConversation(conversationId),
    enabled: !!conversationId,
  })

  const sendMessageMutation = useMutation({
    mutationFn: (msg) => aiAPI.sendMessage(conversationId, msg),
    onSuccess: () => {
      setMessage('')
      refetch()
    },
  })

  const handleSendMessage = () => {
    if (!message.trim()) return
    setIsLoading(true)
    sendMessageMutation.mutate(message, {
      onSettled: () => setIsLoading(false),
    })
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [conversation?.data?.messages])

  if (!conversation) {
    return <div className="text-center py-12">Loading...</div>
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
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 p-4">
        <div className="flex gap-2">
          <Input
            placeholder="Ask SMART AI..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
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