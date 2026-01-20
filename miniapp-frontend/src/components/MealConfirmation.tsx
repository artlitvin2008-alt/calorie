/**
 * MealConfirmation component - Confirm and adjust meal analysis results
 */
import { useState, useEffect } from 'react'
import { AnalysisResult, Ingredient } from '../lib/api'
import { useMealsStore } from '../store/mealsStore'
import LoadingSpinner from './LoadingSpinner'

interface MealConfirmationProps {
  analysis: AnalysisResult
  onSave: () => void
  onCancel: () => void
}

const MealConfirmation = ({ analysis, onSave, onCancel }: MealConfirmationProps) => {
  const [ingredients, setIngredients] = useState<Ingredient[]>(analysis.ingredients)
  const [mealTime, setMealTime] = useState<string>('lunch')
  const [dishName, setDishName] = useState(analysis.dish_name || '')
  const { createMeal, isLoading } = useMealsStore()

  // Calculate total nutrition
  const totalNutrition = ingredients.reduce(
    (acc, ing) => ({
      calories: acc.calories + ing.calories,
      protein: acc.protein + ing.protein,
      fats: acc.fats + ing.fats,
      carbs: acc.carbs + ing.carbs,
    }),
    { calories: 0, protein: 0, fats: 0, carbs: 0 }
  )

  // Determine meal time based on current hour
  useEffect(() => {
    const hour = new Date().getHours()
    if (hour < 11) setMealTime('breakfast')
    else if (hour < 16) setMealTime('lunch')
    else if (hour < 21) setMealTime('dinner')
    else setMealTime('snack')
  }, [])

  const handleWeightChange = (index: number, newWeight: number) => {
    const ingredient = ingredients[index]
    const ratio = newWeight / ingredient.weight
    
    const updatedIngredient = {
      ...ingredient,
      weight: newWeight,
      calories: Math.round(ingredient.calories * ratio),
      protein: Math.round(ingredient.protein * ratio * 10) / 10,
      fats: Math.round(ingredient.fats * ratio * 10) / 10,
      carbs: Math.round(ingredient.carbs * ratio * 10) / 10,
    }

    const newIngredients = [...ingredients]
    newIngredients[index] = updatedIngredient
    setIngredients(newIngredients)
  }

  const handleSave = async () => {
    try {
      await createMeal({
        meal_time: mealTime,
        ingredients,
        photo_path: analysis.photo_path,
        dish_name: dishName,
      })
      onSave()
    } catch (error) {
      console.error('Failed to save meal:', error)
    }
  }

  return (
    <div className="fixed inset-0 bg-white dark:bg-gray-900 z-50 overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 p-4 flex justify-between items-center">
        <button
          onClick={onCancel}
          className="text-primary font-medium"
          disabled={isLoading}
        >
          Cancel
        </button>
        <h2 className="text-lg font-bold">Confirm Meal</h2>
        <button
          onClick={handleSave}
          className="text-primary font-medium"
          disabled={isLoading}
        >
          {isLoading ? 'Saving...' : 'Save'}
        </button>
      </div>

      <div className="p-4">
        {/* Photo Preview */}
        {analysis.photo_path && (
          <div className="mb-4">
            <img
              src={analysis.photo_path}
              alt="Meal"
              className="w-full h-48 object-cover rounded-xl"
            />
          </div>
        )}

        {/* Dish Name */}
        <div className="ios-card p-4 mb-4">
          <label className="block text-sm font-medium mb-2">Dish Name</label>
          <input
            type="text"
            value={dishName}
            onChange={(e) => setDishName(e.target.value)}
            placeholder="Enter dish name"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-transparent"
          />
        </div>

        {/* Meal Time */}
        <div className="ios-card p-4 mb-4">
          <label className="block text-sm font-medium mb-2">Meal Time</label>
          <div className="grid grid-cols-4 gap-2">
            {['breakfast', 'lunch', 'dinner', 'snack'].map((time) => (
              <button
                key={time}
                onClick={() => setMealTime(time)}
                className={`py-2 px-3 rounded-lg text-sm font-medium capitalize ${
                  mealTime === time
                    ? 'bg-primary text-white'
                    : 'bg-gray-100 dark:bg-gray-800'
                }`}
              >
                {time}
              </button>
            ))}
          </div>
        </div>

        {/* Total Nutrition */}
        <div className="ios-card p-4 mb-4">
          <h3 className="font-semibold mb-3">Total Nutrition</h3>
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{Math.round(totalNutrition.calories)}</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">kcal</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-success">{totalNutrition.protein.toFixed(1)}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Protein</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-warning">{totalNutrition.fats.toFixed(1)}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Fats</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-info">{totalNutrition.carbs.toFixed(1)}g</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Carbs</div>
            </div>
          </div>
        </div>

        {/* Ingredients */}
        <div className="ios-card p-4">
          <h3 className="font-semibold mb-3">Adjust Ingredients</h3>
          <div className="space-y-4">
            {ingredients.map((ingredient, index) => (
              <div key={index} className="border-b border-gray-200 dark:border-gray-800 pb-4 last:border-0">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">{ingredient.name}</span>
                  <span className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
                    {ingredient.calories} kcal
                  </span>
                </div>
                
                {/* Weight Slider */}
                <div className="mb-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-secondary-light dark:text-text-secondary-dark">Weight</span>
                    <span className="font-medium">{ingredient.weight}g</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max={ingredient.weight * 3}
                    value={ingredient.weight}
                    onChange={(e) => handleWeightChange(index, parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                {/* Macros */}
                <div className="flex gap-4 text-xs text-text-secondary-light dark:text-text-secondary-dark">
                  <span>P: {ingredient.protein.toFixed(1)}g</span>
                  <span>F: {ingredient.fats.toFixed(1)}g</span>
                  <span>C: {ingredient.carbs.toFixed(1)}g</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <LoadingSpinner />
          </div>
        )}
      </div>
    </div>
  )
}

export default MealConfirmation
