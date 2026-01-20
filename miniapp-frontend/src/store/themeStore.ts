/**
 * Theme store using Zustand
 */
import { create } from 'zustand'
import type { Theme } from '../lib/theme'
import { getDefaultTheme, applyTheme } from '../lib/theme'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

export const useThemeStore = create<ThemeState>((set, get) => ({
  theme: getDefaultTheme(),
  
  setTheme: (theme: Theme) => {
    applyTheme(theme)
    set({ theme })
  },
  
  toggleTheme: () => {
    const currentTheme = get().theme
    const newTheme = getDefaultTheme(!currentTheme.isDark)
    applyTheme(newTheme)
    set({ theme: newTheme })
  },
}))
