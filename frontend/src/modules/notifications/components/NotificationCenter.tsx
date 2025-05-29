import React, { useState } from 'react';
import { Bell, Check, Trash2, X } from 'lucide-react';
import * as Popover from '@radix-ui/react-popover';
import * as ScrollArea from '@radix-ui/react-scroll-area';
import * as Tabs from '@radix-ui/react-tabs';
import { useTranslation } from 'react-i18next';
import { useNotifications } from '../context/NotificationContext';
import { Notification } from '../types';

const NotificationCenter: React.FC = () => {
  const { t } = useTranslation();
  const { 
    notifications, 
    unreadCount, 
    markAsRead, 
    markAllAsRead, 
    clearNotifications 
  } = useNotifications();
  const [open, setOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');

  const filteredNotifications = notifications.filter(notification => {
    if (activeTab === 'all') return true;
    if (activeTab === 'unread') return !notification.read;
    return notification.source === activeTab;
  });

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <span className="text-yellow-500">⚠️</span>;
      case 'error':
        return <span className="text-red-500">❌</span>;
      case 'success':
        return <span className="text-green-500">✅</span>;
      default:
        return <span className="text-blue-500">ℹ️</span>;
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    markAsRead(notification.id);
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  return (
    <Popover.Root open={open} onOpenChange={setOpen}>
      <Popover.Trigger asChild>
        <button 
          className="relative inline-flex items-center justify-center rounded-full p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none"
          aria-label={t('notifications.title')}
        >
          <Bell className="h-6 w-6" />
          {unreadCount > 0 && (
            <span className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-medium text-white">
              {unreadCount}
            </span>
          )}
        </button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content 
          className="w-96 rounded-md border border-gray-200 bg-white shadow-md"
          sideOffset={5}
          align="end"
        >
          <div className="flex items-center justify-between border-b border-gray-200 p-4">
            <h3 className="text-lg font-medium text-gray-900">{t('notifications.title')}</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => markAllAsRead()}
                className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
                title={t('notifications.markAllAsRead')}
              >
                <Check className="h-5 w-5" />
              </button>
              <button
                onClick={() => clearNotifications()}
                className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-500"
                title={t('notifications.clearAll')}
              >
                <Trash2 className="h-5 w-5" />
              </button>
              <Popover.Close className="rounded-md p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-500">
                <X className="h-5 w-5" />
              </Popover.Close>
            </div>
          </div>
          
          <Tabs.Root value={activeTab} onValueChange={setActiveTab}>
            <Tabs.List className="flex border-b border-gray-200">
              <Tabs.Trigger
                value="all"
                className={`flex-1 py-2 text-sm font-medium ${
                  activeTab === 'all' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t('notifications.all')}
              </Tabs.Trigger>
              <Tabs.Trigger
                value="unread"
                className={`flex-1 py-2 text-sm font-medium ${
                  activeTab === 'unread' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t('notifications.unread')}
              </Tabs.Trigger>
              <Tabs.Trigger
                value="legal"
                className={`flex-1 py-2 text-sm font-medium ${
                  activeTab === 'legal' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t('notifications.legal')}
              </Tabs.Trigger>
              <Tabs.Trigger
                value="compliance"
                className={`flex-1 py-2 text-sm font-medium ${
                  activeTab === 'compliance' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {t('notifications.compliance')}
              </Tabs.Trigger>
            </Tabs.List>
            
            <ScrollArea.Root className="h-80 overflow-hidden">
              <ScrollArea.Viewport className="h-full w-full">
                {filteredNotifications.length === 0 ? (
                  <div className="flex h-full items-center justify-center p-4 text-center text-gray-500">
                    {t('notifications.empty')}
                  </div>
                ) : (
                  <div className="divide-y divide-gray-200">
                    {filteredNotifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`cursor-pointer p-4 transition-colors ${
                          notification.read ? 'bg-white' : 'bg-blue-50'
                        } hover:bg-gray-50`}
                        onClick={() => handleNotificationClick(notification)}
                      >
                        <div className="flex items-start">
                          <div className="mr-3 mt-1">
                            {getNotificationIcon(notification.type)}
                          </div>
                          <div className="flex-1">
                            <p className={`text-sm ${notification.read ? 'text-gray-700' : 'font-medium text-gray-900'}`}>
                              {notification.message}
                            </p>
                            <p className="mt-1 text-xs text-gray-500">
                              {new Date(notification.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </ScrollArea.Viewport>
              <ScrollArea.Scrollbar 
                className="flex w-2.5 touch-none select-none bg-gray-100 p-0.5"
                orientation="vertical"
              >
                <ScrollArea.Thumb className="relative flex-1 rounded-full bg-gray-300" />
              </ScrollArea.Scrollbar>
            </ScrollArea.Root>
          </Tabs.Root>
          
          <Popover.Arrow className="fill-white" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  );
};

export default NotificationCenter;
