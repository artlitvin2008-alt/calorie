/**
 * Analytics page - Charts and trends
 */
import { useState, useEffect } from 'react'
import { apiClient } from '../lib/api'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorMessage from '../components/ErrorMessage'

type Period = 'week' | 'month' | 'year'
type ChartTab = 'weight' | 'calories'

interface WeightDataPoint {
  date: string
  weight: number
}

interface CalorieDataPoint {
  date: string
  calories: number
}

const AnalyticsPage = () => {
  const [period, setPeriod] = useState<Period>('week')
  const [activeTab, setActiveTab] = useState<ChartTab>('weight')
  const [weightData, setWeightData] = useState<WeightDataPoint[]>([])
  const [calorieData, setCalorieData] = useState<CalorieDataPoint[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchData()
  }, [period, activeTab])

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      if (activeTab === 'weight') {
        const data = await apiClient.getWeightAnalytics(period)
        setWeightData(data)
      } else {
        const data = await apiClient.getCalorieAnalytics(period)
        setCalorieData(data)
      }
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load analytics data')
    } finally {
      setIsLoading(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    if (period === 'week') {
      return date.toLocaleDateString('en-US', { weekday: 'short' })
    } else if (period === 'month') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    } else {
      return date.toLocaleDateString('en-US', { month: 'short' })
    }
  }

  return (
    <div className="container mx-auto px-4 py-6 pb-24">
      <h1 className="text-2xl font-bold mb-6">Analytics</h1>

      {/* Chart Tabs */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab('weight')}
          className={`flex-1 py-3 px-4 rounded-xl font-medium transition-colors ${
            activeTab === 'weight'
              ? 'bg-primary text-white'
              : 'bg-gray-100 dark:bg-gray-800'
          }`}
        >
          Weight
        </button>
        <button
          onClick={() => setActiveTab('calories')}
          className={`flex-1 py-3 px-4 rounded-xl font-medium transition-colors ${
            activeTab === 'calories'
              ? 'bg-primary text-white'
              : 'bg-gray-100 dark:bg-gray-800'
          }`}
        >
          Calories
        </button>
      </div>

      {/* Period Selector */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setPeriod('week')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            period === 'week'
              ? 'bg-primary text-white'
              : 'bg-gray-100 dark:bg-gray-800'
          }`}
        >
          Week
        </button>
        <button
          onClick={() => setPeriod('month')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            period === 'month'
              ? 'bg-primary text-white'
              : 'bg-gray-100 dark:bg-gray-800'
          }`}
        >
          Month
        </button>
        <button
          onClick={() => setPeriod('year')}
          className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
            period === 'year'
              ? 'bg-primary text-white'
              : 'bg-gray-100 dark:bg-gray-800'
          }`}
        >
          Year
        </button>
      </div>

      {/* Chart */}
      <div className="ios-card p-4 mb-6">
        <h2 className="text-lg font-semibold mb-4">
          {activeTab === 'weight' ? 'Weight Trend' : 'Calorie Consumption'}
        </h2>
        
        {isLoading ? (
          <div className="h-64 flex items-center justify-center">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="h-64 flex items-center justify-center">
            <ErrorMessage message={error} />
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              {activeTab === 'weight' ? (
                <LineChart data={weightData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    stroke="#9ca3af"
                  />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    labelFormatter={formatDate}
                    formatter={(value: number) => [`${value} kg`, 'Weight']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="weight" 
                    stroke="#3b82f6" 
                    strokeWidth={2}
                    dot={{ fill: '#3b82f6', r: 4 }}
                  />
                </LineChart>
              ) : (
                <BarChart data={calorieData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="date" 
                    tickFormatter={formatDate}
                    stroke="#9ca3af"
                  />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip 
                    labelFormatter={formatDate}
                    formatter={(value: number) => [`${value} kcal`, 'Calories']}
                  />
                  <Bar 
                    dataKey="calories" 
                    fill="#3b82f6" 
                    radius={[8, 8, 0, 0]}
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Insights */}
      <div className="ios-card p-4">
        <h2 className="text-lg font-semibold mb-4">💡 Insights</h2>
        <div className="space-y-3">
          <div className="p-3 bg-blue-50 dark:bg-blue-900 dark:bg-opacity-20 rounded-lg">
            <p className="text-sm">
              {activeTab === 'weight' 
                ? 'Your weight trend shows consistent progress. Keep up the great work!'
                : 'Your average calorie intake is within your target range. Maintain this balance for optimal results.'}
            </p>
          </div>
          <div className="p-3 bg-green-50 dark:bg-green-900 dark:bg-opacity-20 rounded-lg">
            <p className="text-sm">
              {activeTab === 'weight'
                ? 'Tip: Regular weigh-ins help track progress more accurately.'
                : 'Tip: Consistent meal timing can help regulate your metabolism.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyticsPage

