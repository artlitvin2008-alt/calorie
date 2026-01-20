/**
 * Dashboard page - Main screen with daily stats
 */
import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useUserStore } from '../store/userStore'
import { useMealsStore } from '../store/mealsStore'
import MealCard from '../components/MealCard'
import MealAddModal from '../components/MealAddModal'

const DashboardPage = () => {
  const location = useLocation()
  const { profile, dailyStats, fetchProfile, fetchDailyStats, isLoading } = useUserStore()
  const { meals, fetchMeals, isLoading: mealsLoading } = useMealsStore()
  const [showAddModal, setShowAddModal] = useState(false)

  // Fetch data on mount and when returning to dashboard
  useEffect(() => {
    fetchProfile()
    fetchDailyStats()
    fetchMeals()
  }, [location.pathname])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary-light dark:text-text-secondary-dark">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">
          👋 Hello, {profile?.first_name || 'User'}!
        </h1>
        <p className="text-text-secondary-light dark:text-text-secondary-dark">
          Track your nutrition and reach your goals
        </p>
      </div>

      {/* Daily Stats Card */}
      {dailyStats && (
        <div className="ios-card p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Today's Progress</h2>
          
          {/* Calories Progress */}
          <div className="mb-4">
            <div className="flex justify-between mb-2">
              <span className="text-sm">Calories</span>
              <span className="text-sm font-medium">
                {dailyStats.consumed.calories} / {dailyStats.goals.calories} kcal
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className="bg-primary h-2 rounded-full transition-all"
                style={{ width: `${Math.min(dailyStats.progress.calories, 100)}%` }}
              />
            </div>
          </div>

          {/* Macros */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary">{dailyStats.consumed.protein}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Protein</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-warning">{dailyStats.consumed.fats}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Fats</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-success">{dailyStats.consumed.carbs}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Carbs</div>
            </div>
          </div>
        </div>
      )}

      {/* Add Meal Button */}
      <button 
        className="ios-button-primary w-full mb-6"
        onClick={() => setShowAddModal(true)}
      >
        + Add Meal
      </button>

      {/* Add Meal Modal */}
      <MealAddModal 
        isOpen={showAddModal} 
        onClose={() => setShowAddModal(false)} 
      />

      {/* Recent Meals */}
      <div className="ios-card p-4">
        <h2 className="text-lg font-semibold mb-4">Recent Meals</h2>
        {mealsLoading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          </div>
        ) : meals.length > 0 ? (
          <div>
            {meals.slice(0, 3).map(meal => (
              <MealCard key={meal.id} meal={meal} />
            ))}
          </div>
        ) : (
          <p className="text-center text-text-secondary-light dark:text-text-secondary-dark py-8">
            No meals logged today. Start by adding your first meal!
          </p>
        )}
      </div>
    </div>
  )
}

export default DashboardPage
