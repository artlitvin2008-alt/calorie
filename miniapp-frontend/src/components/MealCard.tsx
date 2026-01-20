/**
 * MealCard component - Display meal information
 */
import { Meal } from '../lib/api'

interface MealCardProps {
  meal: Meal
  onClick?: () => void
}

const MealCard = ({ meal, onClick }: MealCardProps) => {
  const formatTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  const getMealIcon = (mealTime: string) => {
    switch (mealTime) {
      case 'breakfast': return '🌅'
      case 'lunch': return '☀️'
      case 'dinner': return '🌙'
      case 'snack': return '🍎'
      default: return '🍽️'
    }
  }

  return (
    <div 
      className="ios-card p-4 mb-3 cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <div className="flex gap-3">
        {/* Meal Photo or Icon */}
        <div className="flex-shrink-0">
          {meal.photo_path ? (
            <img 
              src={meal.photo_path} 
              alt={meal.dish_name || 'Meal'} 
              className="w-16 h-16 rounded-lg object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-3xl">
              {getMealIcon(meal.meal_time)}
            </div>
          )}
        </div>

        {/* Meal Info */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h3 className="font-semibold truncate">
              {meal.dish_name || meal.ingredients.map(i => i.name).join(', ')}
            </h3>
            <span className="text-sm text-text-secondary-light dark:text-text-secondary-dark ml-2">
              {formatTime(meal.created_at)}
            </span>
          </div>
          
          <div className="flex items-center gap-2 text-sm text-text-secondary-light dark:text-text-secondary-dark">
            <span className="font-medium text-primary">{meal.calories} kcal</span>
            <span>•</span>
            <span>P: {meal.protein}g</span>
            <span>•</span>
            <span>F: {meal.fats}g</span>
            <span>•</span>
            <span>C: {meal.carbs}g</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default MealCard
