import axios from 'axios';
import { API_BASE_URL } from '../../../constants';
import { Notification } from '../types';

const mockNotifications: Notification[] = [
  {
    id: '1',
    message: 'New contract uploaded: Service Agreement with Acme Corp',
    type: 'info',
    read: false,
    created_at: new Date(Date.now() - 3600000).toISOString(),
    source: 'legal'
  },
  {
    id: '2',
    message: 'PEP match found for client: Global Trading LLC',
    type: 'warning',
    read: false,
    created_at: new Date(Date.now() - 7200000).toISOString(),
    source: 'compliance',
    link: '/compliance/pep-matches/2'
  },
  {
    id: '3',
    message: 'Contract expiring in 30 days: TechStart Inc. NDA',
    type: 'warning',
    read: true,
    created_at: new Date(Date.now() - 86400000).toISOString(),
    source: 'legal',
    link: '/legal/contracts/3'
  },
  {
    id: '4',
    message: 'Weekly compliance report generated',
    type: 'success',
    read: true,
    created_at: new Date(Date.now() - 172800000).toISOString(),
    source: 'compliance',
    link: '/compliance/reports/4'
  }
];

/**
 * Get all notifications for the current user
 */
export const getNotifications = async (): Promise<Notification[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/notifications`);
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications:', error);
    return mockNotifications;
  }
};

/**
 * Mark a notification as read
 */
export const markNotificationAsRead = async (id: string): Promise<void> => {
  try {
    await axios.put(`${API_BASE_URL}/notifications/${id}/read`);
  } catch (error) {
    console.error(`Error marking notification ${id} as read:`, error);
    const index = mockNotifications.findIndex(n => n.id === id);
    if (index !== -1) {
      mockNotifications[index].read = true;
    }
  }
};

/**
 * Mark all notifications as read
 */
export const markAllNotificationsAsRead = async (): Promise<void> => {
  try {
    await axios.put(`${API_BASE_URL}/notifications/read-all`);
  } catch (error) {
    console.error('Error marking all notifications as read:', error);
    mockNotifications.forEach(n => n.read = true);
  }
};

/**
 * Clear all notifications
 */
export const clearAllNotifications = async (): Promise<void> => {
  try {
    await axios.delete(`${API_BASE_URL}/notifications/clear-all`);
  } catch (error) {
    console.error('Error clearing all notifications:', error);
    mockNotifications.length = 0;
  }
};
