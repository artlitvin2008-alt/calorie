/**
 * Diary page - Meal history with date navigation
 */
import { useEffect, useState } from 'react'
import { useMealsStore } from '../store/mealsStore'
import { Meal } from '../lib/api'
import DateSwitcher from '../components/DateSwitcher'
import MealCard from '../components/MealCard'

const DiaryPage = () => {
  const { meals, selectedDate, setSelectedDate, deleteMeal, isLoading } = useMealsStore()
  const [swipedMealId, setSwipedMealId] = useState<number | null>(null)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [mealToDelete, setMealToDelete] = useState<number | null>(null)

  useEffect(() => {
    // Meals are fetched automatically when selectedDate changes in store
  }, [selectedDate])

  // Group meals by meal_time
  const groupedMeals = meals.reduce((acc, meal) => {
    const time = meal.meal_time
    if (!acc[time]) {
      acc[time] = []
    }
    acc[time].push(meal)
    return acc
  }, {} as Record<string, Meal[]>)

  const mealTimeOrder = ['breakfast', 'lunch', 'dinner', 'snack']
  const mealTimeLabels = {
    breakfast: '🌅 Breakfast',
    lunch: '☀️ Lunch',
    dinner: '🌙 Dinner',
    snack: '🍎 Snacks',
  }

  const handleDeleteClick = (mealId: number) => {
    setMealToDelete(mealId)
    setShowDeleteConfirm(true)
  }

  const confirmDelete = async () => {
    if (mealToDelete) {
      try {
        await deleteMeal(mealToDelete)
        setShowDeleteConfirm(false)
        setMealToDelete(null)
        setSwipedMealId(null)
      } catch (error) {
        console.error('Failed to delete meal:', error)
      }
    }
  }

  const cancelDelete = () => {
    setShowDeleteConfirm(false)
    setMealToDelete(null)
  }

  return (
    <div className="container mx-auto px-4 py-6 pb-24">
      <h1 className="text-2xl font-bold mb-6">Food Diary</h1>

      {/* Date Selector */}
      <div className="mb-6">
        <DateSwitcher 
          selectedDate={selectedDate} 
          onDateChange={setSelectedDate} 
        />
      </div>

      {/* Meals List */}
      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary-light dark:text-text-secondary-dark">Loading meals...</p>
        </div>
      ) : meals.length > 0 ? (
        <div className="space-y-6">
          {mealTimeOrder.map((mealTime) => {
            const mealsForTime = groupedMeals[mealTime]
            if (!mealsForTime || mealsForTime.length === 0) return null

            return (
              <div key={mealTime}>
                <h2 className="text-lg font-semibold mb-3">
                  {mealTimeLabels[mealTime as keyof typeof mealTimeLabels]}
                </h2>
                <div className="space-y-3">
                  {mealsForTime.map((meal) => (
                    <div 
                      key={meal.id} 
                      className="relative overflow-hidden"
                      onTouchStart={(e) => {
                        const touch = e.touches[0]
                        const startX = touch.clientX
                        
                        const handleTouchMove = (e: TouchEvent) => {
                          const touch = e.touches[0]
                          const deltaX = startX - touch.clientX
                          
                          if (deltaX > 50) {
                            setSwipedMealId(meal.id)
                          } else if (deltaX < -50) {
                            setSwipedMealId(null)
                          }
                        }
                        
                        const handleTouchEnd = () => {
                          document.removeEventListener('touchmove', handleTouchMove)
                          document.removeEventListener('touchend', handleTouchEnd)
                        }
                        
                        document.addEventListener('touchmove', handleTouchMove)
                        document.addEventListener('touchend', handleTouchEnd)
                      }}
                    >
                      <div 
                        className={`transition-transform duration-200 ${
                          swipedMealId === meal.id ? '-translate-x-20' : ''
                        }`}
                      >
                        <MealCard meal={meal} />
                      </div>
                      
                      {/* Delete Button */}
                      {swipedMealId === meal.id && (
                        <button
                          onClick={() => handleDeleteClick(meal.id)}
                          className="absolute right-2 top-1/2 -translate-y-1/2 bg-red-500 text-white px-4 py-2 rounded-lg font-medium"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <div className="ios-card p-8 text-center">
          <div className="text-6xl mb-4">📝</div>
          <p className="text-text-secondary-light dark:text-text-secondary-dark">
            No meals logged for this date
          </p>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-sm w-full">
            <h3 className="text-lg font-bold mb-2">Delete Meal?</h3>
            <p className="text-text-secondary-light dark:text-text-secondary-dark mb-6">
              Are you sure you want to delete this meal? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={cancelDelete}
                className="flex-1 py-3 px-6 bg-gray-200 dark:bg-gray-800 rounded-xl font-medium"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="flex-1 py-3 px-6 bg-red-500 text-white rounded-xl font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DiaryPage

