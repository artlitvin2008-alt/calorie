/**
 * User store using Zustand
 */
import { create } from 'zustand'
import { apiClient, UserProfile, DailyStats } from '../lib/api'

interface UserState {
  profile: UserProfile | null
  dailyStats: DailyStats | null
  isLoading: boolean
  error: string | null
  
  // Actions
  fetchProfile: () => Promise<void>
  updateProfile: (data: Partial<UserProfile>) => Promise<void>
  fetchDailyStats: () => Promise<void>
  clearError: () => void
}

export const useUserStore = create<UserState>((set, get) => ({
  profile: null,
  dailyStats: null,
  isLoading: false,
  error: null,

  fetchProfile: async () => {
    set({ isLoading: true, error: null })
    try {
      const profile = await apiClient.getUserProfile()
      set({ profile, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch profile',
        isLoading: false 
      })
    }
  },

  updateProfile: async (data: Partial<UserProfile>) => {
    set({ isLoading: true, error: null })
    try {
      const profile = await apiClient.updateUserProfile(data)
      set({ profile, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to update profile',
        isLoading: false 
      })
      throw error
    }
  },

  fetchDailyStats: async () => {
    set({ isLoading: true, error: null })
    try {
      const dailyStats = await apiClient.getTodayStats()
      set({ dailyStats, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch daily stats',
        isLoading: false 
      })
    }
  },

  clearError: () => set({ error: null }),
}))
