/**
 * CameraCapture component - Capture photos using device camera
 */
import { useRef, useState, useEffect } from 'react'

interface CameraCaptureProps {
  onCapture: (file: File) => void
  onCancel: () => void
}

const CameraCapture = ({ onCapture, onCancel }: CameraCaptureProps) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [permissionDenied, setPermissionDenied] = useState(false)

  useEffect(() => {
    startCamera()
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' },
        audio: false,
      })
      
      setStream(mediaStream)
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
      setError(null)
      setPermissionDenied(false)
    } catch (err: any) {
      console.error('Camera error:', err)
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setPermissionDenied(true)
        setError('Camera permission denied. Please enable camera access in your browser settings.')
      } else if (err.name === 'NotFoundError') {
        setError('No camera found on this device.')
      } else {
        setError('Failed to access camera. Please try again.')
      }
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return

    const video = videoRef.current
    const canvas = canvasRef.current
    
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    ctx.drawImage(video, 0, 0)
    
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.9)
    setCapturedImage(imageDataUrl)
    stopCamera()
  }

  const retake = () => {
    setCapturedImage(null)
    startCamera()
  }

  const confirm = () => {
    if (!capturedImage || !canvasRef.current) return

    canvasRef.current.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `photo_${Date.now()}.jpg`, { type: 'image/jpeg' })
        onCapture(file)
      }
    }, 'image/jpeg', 0.9)
  }

  if (permissionDenied) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-sm w-full">
          <div className="text-center mb-4">
            <div className="text-6xl mb-4">📷</div>
            <h3 className="text-lg font-semibold mb-2">Camera Access Required</h3>
            <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
              {error}
            </p>
          </div>
          <button
            onClick={onCancel}
            className="ios-button-primary w-full"
          >
            Close
          </button>
        </div>
      </div>
    )
  }

  if (error && !permissionDenied) {
    return (
      <div className="fixed inset-0 bg-black z-50 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-sm w-full">
          <div className="text-center mb-4">
            <div className="text-6xl mb-4">⚠️</div>
            <h3 className="text-lg font-semibold mb-2">Camera Error</h3>
            <p className="text-sm text-text-secondary-light dark:text-text-secondary-dark">
              {error}
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={startCamera}
              className="ios-button-secondary flex-1"
            >
              Retry
            </button>
            <button
              onClick={onCancel}
              className="ios-button-primary flex-1"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* Camera View or Captured Image */}
      <div className="flex-1 relative">
        {capturedImage ? (
          <img 
            src={capturedImage} 
            alt="Captured" 
            className="w-full h-full object-contain"
          />
        ) : (
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full h-full object-cover"
          />
        )}
        
        {/* Hidden canvas for capture */}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      {/* Controls */}
      <div className="bg-black bg-opacity-80 p-6">
        {capturedImage ? (
          <div className="flex gap-3">
            <button
              onClick={retake}
              className="flex-1 py-3 px-6 bg-gray-700 text-white rounded-xl font-medium"
            >
              Retake
            </button>
            <button
              onClick={confirm}
              className="flex-1 py-3 px-6 bg-primary text-white rounded-xl font-medium"
            >
              Use Photo
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <button
              onClick={onCancel}
              className="py-3 px-6 text-white font-medium"
            >
              Cancel
            </button>
            <button
              onClick={capturePhoto}
              className="w-16 h-16 bg-white rounded-full border-4 border-gray-300 hover:border-primary transition-colors"
            />
            <div className="w-20" /> {/* Spacer for centering */}
          </div>
        )}
      </div>
    </div>
  )
}

export default CameraCapture
