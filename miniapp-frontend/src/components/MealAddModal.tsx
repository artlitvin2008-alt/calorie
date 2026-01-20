/**
 * MealAddModal component - Modal for adding meals with multiple input options
 */
import { useState, useRef } from 'react'
import CameraCapture from './CameraCapture'
import MealConfirmation from './MealConfirmation'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'
import { useMealsStore } from '../store/mealsStore'

interface MealAddModalProps {
  isOpen: boolean
  onClose: () => void
}

type InputMode = 'options' | 'camera' | 'gallery' | 'manual' | 'analyzing' | 'confirmation'

const MealAddModal = ({ isOpen, onClose }: MealAddModalProps) => {
  const [mode, setMode] = useState<InputMode>('options')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { analyzePhoto, currentAnalysis, isAnalyzing, error, clearError, setCurrentAnalysis } = useMealsStore()

  if (!isOpen) return null

  const handleCameraCapture = async (file: File) => {
    setMode('analyzing')
    try {
      await analyzePhoto(file)
      setMode('confirmation')
    } catch (error) {
      console.error('Failed to analyze photo:', error)
      setMode('options')
    }
  }

  const handleGallerySelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setMode('analyzing')
    try {
      await analyzePhoto(file)
      setMode('confirmation')
    } catch (error) {
      console.error('Failed to analyze photo:', error)
      setMode('options')
    }
  }

  const handleSaveComplete = () => {
    setCurrentAnalysis(null)
    setMode('options')
    onClose()
  }

  const handleCancelConfirmation = () => {
    setCurrentAnalysis(null)
    setMode('options')
  }

  const handleManualSubmit = () => {
    // TODO: Implement manual meal entry
    onClose()
  }

  // Camera mode
  if (mode === 'camera') {
    return (
      <CameraCapture
        onCapture={handleCameraCapture}
        onCancel={() => setMode('options')}
      />
    )
  }

  // Analyzing mode
  if (mode === 'analyzing') {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center">
        <div className="bg-white dark:bg-gray-900 rounded-2xl p-8 text-center">
          <LoadingSpinner />
          <p className="mt-4 text-text-secondary-light dark:text-text-secondary-dark">
            Analyzing your meal...
          </p>
        </div>
      </div>
    )
  }

  // Confirmation mode
  if (mode === 'confirmation' && currentAnalysis) {
    return (
      <MealConfirmation
        analysis={currentAnalysis}
        onSave={handleSaveComplete}
        onCancel={handleCancelConfirmation}
      />
    )
  }

  // Error display
  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-900 rounded-2xl p-6 max-w-sm w-full">
          <ErrorMessage message={error} />
          <button
            onClick={() => {
              clearError()
              setMode('options')
            }}
            className="ios-button-primary w-full mt-4"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  // Options mode
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-40 flex items-end">
      <div className="bg-white dark:bg-gray-900 rounded-t-3xl w-full p-6 animate-slide-up">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Add Meal</h2>
          <button
            onClick={onClose}
            className="text-2xl text-text-secondary-light dark:text-text-secondary-dark"
          >
            ×
          </button>
        </div>

        {/* Options */}
        <div className="space-y-3">
          {/* Camera Option */}
          <button
            onClick={() => setMode('camera')}
            className="w-full ios-card p-4 flex items-center gap-4 hover:shadow-md transition-shadow"
          >
            <div className="w-12 h-12 bg-primary bg-opacity-10 rounded-full flex items-center justify-center text-2xl">
              📷
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold">Take Photo</h3>
              <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
                Capture your meal with camera
              </p>
            </div>
          </button>

          {/* Gallery Option */}
          <button
            onClick={() => fileInputRef.current?.click()}
            className="w-full ios-card p-4 flex items-center gap-4 hover:shadow-md transition-shadow"
          >
            <div className="w-12 h-12 bg-success bg-opacity-10 rounded-full flex items-center justify-center text-2xl">
              🖼️
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold">Choose from Gallery</h3>
              <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
                Select an existing photo
              </p>
            </div>
          </button>

          {/* Manual Option */}
          <button
            onClick={() => setMode('manual')}
            className="w-full ios-card p-4 flex items-center gap-4 hover:shadow-md transition-shadow"
          >
            <div className="w-12 h-12 bg-warning bg-opacity-10 rounded-full flex items-center justify-center text-2xl">
              ✏️
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold">Enter Manually</h3>
              <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
                Type in meal details
              </p>
            </div>
          </button>
        </div>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleGallerySelect}
          className="hidden"
        />
      </div>
    </div>
  )
}

export default MealAddModal
