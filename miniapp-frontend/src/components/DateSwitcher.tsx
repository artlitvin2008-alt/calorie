/**
 * DateSwitcher component - Navigate between dates
 */
interface DateSwitcherProps {
  selectedDate: string
  onDateChange: (date: string) => void
}

const DateSwitcher = ({ selectedDate, onDateChange }: DateSwitcherProps) => {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday'
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
      })
    }
  }

  const changeDate = (days: number) => {
    const date = new Date(selectedDate)
    date.setDate(date.getDate() + days)
    onDateChange(date.toISOString().split('T')[0])
  }

  const isToday = () => {
    const today = new Date().toISOString().split('T')[0]
    return selectedDate === today
  }

  return (
    <div className="ios-card p-4 flex items-center justify-between">
      <button
        onClick={() => changeDate(-1)}
        className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
      </button>

      <div className="flex-1 text-center">
        <div className="text-lg font-semibold">{formatDate(selectedDate)}</div>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => onDateChange(e.target.value)}
          className="text-sm text-text-secondary-light dark:text-text-secondary-dark cursor-pointer"
        />
      </div>

      <button
        onClick={() => changeDate(1)}
        disabled={isToday()}
        className={`w-10 h-10 flex items-center justify-center rounded-full transition-colors ${
          isToday() 
            ? 'opacity-30 cursor-not-allowed' 
            : 'hover:bg-gray-100 dark:hover:bg-gray-800'
        }`}
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>
    </div>
  )
}

export default DateSwitcher
