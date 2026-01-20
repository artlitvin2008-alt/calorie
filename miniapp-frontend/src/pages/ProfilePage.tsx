/**
 * Profile page - User settings and preferences
 */
import { useEffect, useState } from 'react'
import { useUserStore } from '../store/userStore'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

const ProfilePage = () => {
  const { profile, fetchProfile, updateProfile, isLoading, error } = useUserStore()
  const [isEditing, setIsEditing] = useState(false)
  const [showSuccess, setShowSuccess] = useState(false)
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})
  const [formData, setFormData] = useState({
    height: 0,
    weight: 0,
    age: 0,
    gender: 'other' as 'male' | 'female' | 'other',
    goals: {
      calories: 2000,
      protein: 150,
      fats: 65,
      carbs: 250,
    },
    notifications_enabled: true,
  })

  useEffect(() => {
    fetchProfile()
  }, [])

  useEffect(() => {
    if (profile) {
      setFormData({
        height: profile.height || 0,
        weight: profile.weight || 0,
        age: profile.age || 0,
        gender: profile.gender || 'other',
        goals: profile.goals,
        notifications_enabled: profile.notifications_enabled,
      })
    }
  }, [profile])

  const validateForm = () => {
    const errors: Record<string, string> = {}

    if (formData.height && (formData.height < 100 || formData.height > 250)) {
      errors.height = 'Height must be between 100 and 250 cm'
    }

    if (formData.weight && (formData.weight < 30 || formData.weight > 300)) {
      errors.weight = 'Weight must be between 30 and 300 kg'
    }

    if (formData.age && (formData.age < 10 || formData.age > 120)) {
      errors.age = 'Age must be between 10 and 120 years'
    }

    if (formData.goals.calories < 1000 || formData.goals.calories > 5000) {
      errors.calories = 'Calories must be between 1000 and 5000'
    }

    if (formData.goals.protein < 20 || formData.goals.protein > 500) {
      errors.protein = 'Protein must be between 20 and 500g'
    }

    if (formData.goals.fats < 20 || formData.goals.fats > 300) {
      errors.fats = 'Fats must be between 20 and 300g'
    }

    if (formData.goals.carbs < 50 || formData.goals.carbs > 800) {
      errors.carbs = 'Carbs must be between 50 and 800g'
    }

    setValidationErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSave = async () => {
    if (!validateForm()) {
      return
    }

    try {
      await updateProfile(formData)
      setIsEditing(false)
      setShowSuccess(true)
      setTimeout(() => setShowSuccess(false), 3000)
    } catch (error) {
      console.error('Failed to update profile:', error)
    }
  }

  const handleNotificationToggle = async () => {
    try {
      await updateProfile({
        notifications_enabled: !formData.notifications_enabled,
      })
      setFormData({
        ...formData,
        notifications_enabled: !formData.notifications_enabled,
      })
    } catch (error) {
      console.error('Failed to update notifications:', error)
    }
  }

  if (isLoading && !profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-6 pb-24">
      <h1 className="text-2xl font-bold mb-6">Profile</h1>

      {/* Success Message */}
      {showSuccess && (
        <div className="mb-4 p-4 bg-green-50 dark:bg-green-900 dark:bg-opacity-20 rounded-xl">
          <p className="text-green-700 dark:text-green-300 text-center font-medium">
            ✓ Profile updated successfully!
          </p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4">
          <ErrorMessage message={error} />
        </div>
      )}

      {/* User Info */}
      <div className="ios-card p-4 mb-6">
        <div className="flex items-center">
          <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center text-white text-2xl font-bold mr-4">
            {profile?.first_name?.[0] || 'U'}
          </div>
          <div>
            <h2 className="text-xl font-semibold">{profile?.first_name || 'User'}</h2>
            <p className="text-text-secondary-light dark:text-text-secondary-dark">
              @{profile?.username || 'username'}
            </p>
          </div>
        </div>
      </div>

      {/* Physical Stats */}
      <div className="ios-card p-4 mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Physical Stats</h2>
          <button
            onClick={() => {
              setIsEditing(!isEditing)
              setValidationErrors({})
            }}
            className="text-primary text-sm font-medium"
          >
            {isEditing ? 'Cancel' : 'Edit'}
          </button>
        </div>

        {isEditing ? (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Height (cm)</label>
              <input
                type="number"
                value={formData.height || ''}
                onChange={(e) => setFormData({ ...formData, height: Number(e.target.value) })}
                className={`w-full px-3 py-2 border rounded-lg bg-transparent ${
                  validationErrors.height ? 'border-red-500' : 'border-gray-300 dark:border-gray-700'
                }`}
                placeholder="170"
              />
              {validationErrors.height && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.height}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Weight (kg)</label>
              <input
                type="number"
                value={formData.weight || ''}
                onChange={(e) => setFormData({ ...formData, weight: Number(e.target.value) })}
                className={`w-full px-3 py-2 border rounded-lg bg-transparent ${
                  validationErrors.weight ? 'border-red-500' : 'border-gray-300 dark:border-gray-700'
                }`}
                placeholder="70"
              />
              {validationErrors.weight && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.weight}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Age</label>
              <input
                type="number"
                value={formData.age || ''}
                onChange={(e) => setFormData({ ...formData, age: Number(e.target.value) })}
                className={`w-full px-3 py-2 border rounded-lg bg-transparent ${
                  validationErrors.age ? 'border-red-500' : 'border-gray-300 dark:border-gray-700'
                }`}
                placeholder="25"
              />
              {validationErrors.age && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.age}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Gender</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-transparent"
              >
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </select>
            </div>

            <button
              onClick={handleSave}
              className="ios-button-primary w-full"
              disabled={isLoading || Object.keys(validationErrors).length > 0}
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.height || '-'}</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Height (cm)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.weight || '-'}</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Weight (kg)</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{profile?.age || '-'}</div>
              <div className="text-xs text-text-secondary-light dark:text-text-secondary-dark">Age</div>
            </div>
          </div>
        )}
      </div>

      {/* Daily Goals */}
      <div className="ios-card p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Daily Goals</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span>Calories</span>
            <span className="font-semibold">{profile?.goals.calories} kcal</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Protein</span>
            <span className="font-semibold">{profile?.goals.protein}g</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Fats</span>
            <span className="font-semibold">{profile?.goals.fats}g</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Carbs</span>
            <span className="font-semibold">{profile?.goals.carbs}g</span>
          </div>
        </div>
      </div>

      {/* Settings */}
      <div className="ios-card p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">Settings</h2>
        <div className="flex justify-between items-center">
          <span>Notifications</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={formData.notifications_enabled}
              onChange={handleNotificationToggle}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary"></div>
          </label>
        </div>
      </div>

      {/* Chat with Trainer */}
      <div className="ios-card p-4">
        <h2 className="text-lg font-semibold mb-2">💬 Chat with AI Trainer</h2>
        <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark mb-4">
          Get personalized nutrition advice and answers to your questions
        </p>
        <button className="ios-button-secondary w-full">
          Start Chat
        </button>
      </div>
    </div>
  )
}

export default ProfilePage

