/**
 * Meals store using Zustand
 */
import { create } from 'zustand'
import { apiClient, Meal, Ingredient, AnalysisResult } from '../lib/api'

interface MealsState {
  meals: Meal[]
  currentAnalysis: AnalysisResult | null
  selectedDate: string
  isLoading: boolean
  isAnalyzing: boolean
  error: string | null
  
  // Actions
  fetchMeals: (date?: string) => Promise<void>
  analyzePhoto: (file: File) => Promise<AnalysisResult>
  analyzeVideo: (file: File) => Promise<AnalysisResult>
  createMeal: (data: {
    meal_time: string
    ingredients: Ingredient[]
    photo_path?: string
    dish_name?: string
  }) => Promise<void>
  updateMeal: (mealId: number, data: {
    meal_time?: string
    ingredients?: Ingredient[]
    dish_name?: string
  }) => Promise<void>
  deleteMeal: (mealId: number) => Promise<void>
  setSelectedDate: (date: string) => void
  setCurrentAnalysis: (analysis: AnalysisResult | null) => void
  clearError: () => void
}

export const useMealsStore = create<MealsState>((set, get) => ({
  meals: [],
  currentAnalysis: null,
  selectedDate: new Date().toISOString().split('T')[0],
  isLoading: false,
  isAnalyzing: false,
  error: null,

  fetchMeals: async (date?: string) => {
    set({ isLoading: true, error: null })
    try {
      const meals = await apiClient.getMeals(date)
      set({ meals, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to fetch meals',
        isLoading: false 
      })
    }
  },

  analyzePhoto: async (file: File) => {
    set({ isAnalyzing: true, error: null })
    try {
      const analysis = await apiClient.analyzePhoto(file)
      set({ currentAnalysis: analysis, isAnalyzing: false })
      return analysis
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to analyze photo',
        isAnalyzing: false 
      })
      throw error
    }
  },

  analyzeVideo: async (file: File) => {
    set({ isAnalyzing: true, error: null })
    try {
      const analysis = await apiClient.analyzeVideo(file)
      set({ currentAnalysis: analysis, isAnalyzing: false })
      return analysis
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to analyze video',
        isAnalyzing: false 
      })
      throw error
    }
  },

  createMeal: async (data) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.createMeal(data)
      // Refresh meals list
      await get().fetchMeals(get().selectedDate)
      set({ currentAnalysis: null, isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to create meal',
        isLoading: false 
      })
      throw error
    }
  },

  updateMeal: async (mealId, data) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.updateMeal(mealId, data)
      // Refresh meals list
      await get().fetchMeals(get().selectedDate)
      set({ isLoading: false })
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to update meal',
        isLoading: false 
      })
      throw error
    }
  },

  deleteMeal: async (mealId) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.deleteMeal(mealId)
      // Remove from local state
      set(state => ({
        meals: state.meals.filter(m => m.id !== mealId),
        isLoading: false
      }))
    } catch (error: any) {
      set({ 
        error: error.response?.data?.message || 'Failed to delete meal',
        isLoading: false 
      })
      throw error
    }
  },

  setSelectedDate: (date: string) => {
    set({ selectedDate: date })
    get().fetchMeals(date)
  },

  setCurrentAnalysis: (analysis: AnalysisResult | null) => {
    set({ currentAnalysis: analysis })
  },

  clearError: () => set({ error: null }),
}))
