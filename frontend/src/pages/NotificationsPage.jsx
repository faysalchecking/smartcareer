import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import notificationsAPI from '../services/notifications'
import Badge from '../components/Badge'
import Button from '../components/Button'

export default function NotificationsPage() {
  const [filter, setFilter] = useState('unread')

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['notifications', filter],
    queryFn: async () => {
      if (filter === 'unread') {
        const response = await notificationsAPI.unread()
        return response.data
      } else {
        const response = await notificationsAPI.list()
        return response.data.results || []
      }
    },
  })

  const notifications = data || []

  const handleMarkAsRead = async (id) => {
    await notificationsAPI.markAsRead(id)
    refetch()
  }

  const handleMarkAllAsRead = async () => {
    await notificationsAPI.markAllAsRead()
    refetch()
  }

  const getChannelIcon = (channel) => {
    const icons = {
      EMAIL: '📧',
      SMS: '📱',
      IN_APP: '🔔',
      WHATSAPP: '💬',
    }
    return icons[channel] || '📬'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleMarkAllAsRead}
            >
              Mark all as read
            </Button>
          </div>

          {/* Filters */}
          <div className="flex gap-2">
            <Button
              variant={filter === 'unread' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilter('unread')}
            >
              Unread
            </Button>
            <Button
              variant={filter === 'all' ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setFilter('all')}
            >
              All
            </Button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-2xl mx-auto px-4 py-8">
        {isLoading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Loading...</p>
          </div>
        ) : notifications.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No notifications</p>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map((notif) => (
              <div
                key={notif.id}
                className={`p-4 rounded-lg border-l-4 ${
                  notif.read_at
                    ? 'bg-white border-gray-200'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">
                        {getChannelIcon(notif.channel)}
                      </span>
                      {notif.subject && (
                        <h3 className="font-semibold text-gray-900">
                          {notif.subject}
                        </h3>
                      )}
                    </div>
                    <p className="text-gray-600 text-sm mb-2">{notif.body}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span>{new Date(notif.created_at).toLocaleString()}</span>
                      {notif.read_at && (
                        <Badge variant="success" size="sm">
                          Read
                        </Badge>
                      )}
                    </div>
                  </div>
                  {!notif.read_at && (
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => handleMarkAsRead(notif.id)}
                    >
                      Mark read
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}