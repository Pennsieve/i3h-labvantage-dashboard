<template>
  <div class="timeline-chart">
    <div class="chart-header">
      <h2>Samples Timeline</h2>
    </div>
    
    <div class="timeline-controls">
      <div class="controls-row">
        <div class="control-group">
          <label>Aggregation:</label>
          <select v-model="aggregation" @change="updateChart" class="control-select">
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
        </div>
        
        <div class="control-group">
          <label>View Mode:</label>
          <select v-model="viewMode" @change="updateChart" class="control-select">
            <option value="counts">Sample Counts</option>
            <option value="cumulative">Cumulative Total</option>
          </select>
        </div>
      </div>
      
      <div class="studies-section">
        <div class="studies-header">
          <label class="section-label">Filter by Studies</label>
          <div class="studies-controls">
            <div class="study-search">
              <input 
                type="text" 
                v-model="studySearchTerm" 
                placeholder="Search studies..." 
                class="search-input"
                @input="filterStudies"
              />
              <span class="search-icon">🔍</span>
            </div>
            <div class="selection-actions">
              <button @click="selectAllStudies" class="btn-action btn-select-all">Select All</button>
              <button @click="deselectAllStudies" class="btn-action btn-clear">Clear All</button>
            </div>
            <div class="study-counter">
              {{ selectedStudies.length }} / {{ availableStudies.length }} selected
            </div>
          </div>
        </div>
        
        <div class="study-filters-container">
          <div class="study-filters" :class="{ 'expanded': showAllStudies }">
            <label v-for="study in filteredStudies" :key="study" class="study-checkbox">
              <input 
                type="checkbox" 
                :value="study"
                v-model="selectedStudies"
                @change="updateChart"
              />
              <span class="study-name" :style="{ color: getStudyColor(study) }">{{ study }}</span>
              <span class="study-sample-count">({{ getStudySampleCount(study) }} samples)</span>
            </label>
          </div>
          
          <button 
            v-if="availableStudies.length > 10" 
            @click="toggleShowAllStudies" 
            class="toggle-studies-btn"
          >
            {{ showAllStudies ? 'Show Less' : `Show All ${availableStudies.length} Studies` }}
          </button>
        </div>
      </div>
    </div>
    
    <div class="chart-container-wrapper">
      <Line 
        v-if="chartData"
        :data="chartData" 
        :options="chartOptions" 
      />
      <div v-else class="no-data">
        Loading chart data...
      </div>
    </div>
    
    <div class="summary-stats">
      <div class="stat-item">
        <span class="stat-label">Total Samples:</span>
        <span class="stat-value">{{ totalSamples }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Date Range:</span>
        <span class="stat-value">{{ dateRange }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">Studies Selected:</span>
        <span class="stat-value">{{ selectedStudies.length }} / {{ availableStudies.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Line } from 'vue-chartjs'
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  Title, 
  Tooltip, 
  Legend,
  TimeScale
} from 'chart.js'
import { format, parseISO } from 'date-fns'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

const props = defineProps({
  executeQuery: Function
})

const availableStudies = ref([])
const selectedStudies = ref([])
const aggregation = ref('week')
const viewMode = ref('counts')
const chartData = ref(null)
const totalSamples = ref(0)
const dateRange = ref('')
const studySearchTerm = ref('')
const showAllStudies = ref(false)
const studySampleCounts = ref({})

const studyColors = {
  'AILC': '#667eea',
  'ACRC': '#f56565',
  'AMC': '#48bb78',
  'APC': '#ed8936',
  'APHL': '#9f7aea',
  'APNC': '#38b2ac',
  'BV': '#ed64a6',
  'CCC': '#f6ad55',
  'CEAL': '#4299e1',
  'CHOP': '#fc8181'
}

const getStudyColor = (study) => {
  return studyColors[study] || `#${Math.floor(Math.random()*16777215).toString(16)}`
}

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
    },
    title: {
      display: false
    },
    tooltip: {
      mode: 'nearest',
      intersect: true,
      callbacks: {
        title: (tooltipItems) => {
          return tooltipItems[0].label
        },
        label: (context) => {
          const prefix = viewMode.value === 'cumulative' ? 'Cumulative' : 'Period'
          return `${context.dataset.label}: ${context.parsed.y} samples (${prefix})`
        }
      }
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Date'
      },
      grid: {
        display: false
      },
      ticks: {
        maxRotation: 45,
        minRotation: 45,
        autoSkip: true,
        maxTicksLimit: 15,
        font: {
          size: 11
        }
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Number of Samples'
      },
      beginAtZero: true,
      ticks: {
        precision: 0
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}))

const loadAvailableStudies = async () => {
  try {
    const result = await props.executeQuery(`
      SELECT DISTINCT STUDY 
      FROM samples 
      WHERE STUDY IS NOT NULL 
      ORDER BY STUDY
    `)
    availableStudies.value = result.map(r => r.STUDY)
    selectedStudies.value = [...availableStudies.value]
  } catch (err) {
    console.error('Failed to load studies:', err)
  }
}

const updateChart = async () => {
  if (selectedStudies.value.length === 0) {
    chartData.value = null
    return
  }
  
  try {
    const studyFilter = selectedStudies.value
      .map(s => `'${s}'`)
      .join(',')
    
    // Build aggregation query based on selection
    let aggregateSelect = ''
    if (aggregation.value === 'day') {
      aggregateSelect = "CAST(VISITDATE AS DATE)"
    } else if (aggregation.value === 'week') {
      aggregateSelect = "DATE_TRUNC('week', CAST(VISITDATE AS DATE))"
    } else {
      aggregateSelect = "DATE_TRUNC('month', CAST(VISITDATE AS DATE))"
    }
    
    const query = `
      SELECT 
        ${aggregateSelect} as period,
        STUDY,
        COUNT(*) as sample_count
      FROM samples
      WHERE VISITDATE IS NOT NULL 
        AND STUDY IN (${studyFilter})
      GROUP BY ${aggregateSelect}, STUDY
      ORDER BY period, STUDY
    `
    
    console.log('Executing query:', query)
    const result = await props.executeQuery(query)
    console.log('Query result:', result)
    
    if (!result || result.length === 0) {
      console.log('No data returned from query')
      chartData.value = {
        labels: [],
        datasets: []
      }
      return
    }
    
    // Group data by period and convert BigInt to Number
    const periodMap = new Map()
    result.forEach(row => {
      const periodKey = String(row.period) // Ensure period is a string
      if (!periodMap.has(periodKey)) {
        periodMap.set(periodKey, {})
      }
      // Convert BigInt to Number
      const count = typeof row.sample_count === 'bigint' 
        ? Number(row.sample_count) 
        : row.sample_count
      periodMap.get(periodKey)[row.STUDY] = count
    })
    
    // Sort periods chronologically
    const sortedPeriods = Array.from(periodMap.keys()).sort()
    
    // Format labels based on aggregation
    const formattedLabels = sortedPeriods.map(period => {
      try {
        console.log('Formatting period:', period)
        
        // Convert period to proper date
        let dateToFormat
        
        // Check if it's a numeric timestamp (milliseconds)
        if (!isNaN(period) && typeof period !== 'string') {
          // It's a numeric timestamp in milliseconds
          dateToFormat = new Date(Number(period))
        } else {
          const periodStr = String(period)
          
          // Check if it's a string that's actually a number (timestamp)
          if (periodStr.match(/^\d+$/)) {
            // It's a timestamp as a string
            dateToFormat = new Date(Number(periodStr))
          } else if (periodStr.includes('T') || periodStr.includes(' ')) {
            // ISO string or date with time
            dateToFormat = new Date(periodStr)
          } else if (periodStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            // Handle YYYY-MM-DD format
            const [year, month, day] = periodStr.split('-')
            dateToFormat = new Date(parseInt(year), parseInt(month) - 1, parseInt(day))
          } else {
            // Try direct parsing
            dateToFormat = new Date(periodStr)
          }
        }
        
        // Check if date is valid
        if (!dateToFormat || isNaN(dateToFormat.getTime())) {
          console.error('Invalid date:', period, 'parsed as:', dateToFormat)
          return String(period).substring(0, 10) // Return first 10 chars as fallback
        }
        
        // Format as MM/DD/YYYY for all aggregation levels
        const month = (dateToFormat.getMonth() + 1).toString().padStart(2, '0')
        const day = dateToFormat.getDate().toString().padStart(2, '0')
        const year = dateToFormat.getFullYear()
        
        if (aggregation.value === 'month') {
          // For monthly, just show MM/YYYY
          return `${month}/${year}`
        } else {
          // For daily and weekly, show MM/DD/YYYY
          return `${month}/${day}/${year}`
        }
        
      } catch (e) {
        console.error('Error formatting date label:', e, 'for period:', period)
        return String(period).substring(0, 10)
      }
    })
    
    // Build datasets for each study
    const datasets = []
    for (const study of selectedStudies.value) {
      let data = sortedPeriods.map(period => {
        const periodData = periodMap.get(period)
        return periodData[study] || 0
      })
      
      // Convert to cumulative if needed
      if (viewMode.value === 'cumulative') {
        let runningTotal = 0
        data = data.map(count => {
          runningTotal += count
          return runningTotal
        })
      }
      
      datasets.push({
        label: study,
        data: data,
        borderColor: getStudyColor(study),
        backgroundColor: getStudyColor(study) + '20',
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        tension: 0.1,
        fill: viewMode.value === 'cumulative' // Fill area under cumulative lines
      })
    }
    
    console.log('Chart data:', { labels: formattedLabels, datasets })
    chartData.value = {
      labels: formattedLabels,
      datasets: datasets
    }
    
    const statsQuery = `
      SELECT 
        COUNT(*) as total,
        MIN(VISITDATE) as min_date,
        MAX(VISITDATE) as max_date
      FROM samples
      WHERE STUDY IN (${studyFilter})
        AND VISITDATE IS NOT NULL
    `
    
    const stats = await props.executeQuery(statsQuery)
    if (stats && stats[0]) {
      // Convert BigInt to Number for totalSamples
      totalSamples.value = typeof stats[0].total === 'bigint' 
        ? Number(stats[0].total) 
        : stats[0].total
      
      // Handle date formatting safely
      try {
        const minDateStr = String(stats[0].min_date)
        const maxDateStr = String(stats[0].max_date)
        
        const minDate = minDateStr && minDateStr !== 'null' 
          ? format(new Date(minDateStr), 'MMM d, yyyy') 
          : 'N/A'
        const maxDate = maxDateStr && maxDateStr !== 'null' 
          ? format(new Date(maxDateStr), 'MMM d, yyyy') 
          : 'N/A'
        
        dateRange.value = `${minDate} - ${maxDate}`
      } catch (e) {
        console.error('Error formatting dates:', e)
        dateRange.value = 'N/A'
      }
    }
    
  } catch (err) {
    console.error('Failed to update chart:', err)
  }
}

const filteredStudies = computed(() => {
  if (!studySearchTerm.value.trim()) {
    return showAllStudies.value ? availableStudies.value : availableStudies.value.slice(0, 10)
  }
  
  const filtered = availableStudies.value.filter(study => 
    study.toLowerCase().includes(studySearchTerm.value.toLowerCase())
  )
  
  return showAllStudies.value ? filtered : filtered.slice(0, 10)
})

const loadStudySampleCounts = async () => {
  try {
    const result = await props.executeQuery(`
      SELECT STUDY, COUNT(*) as count
      FROM samples 
      WHERE STUDY IS NOT NULL 
      GROUP BY STUDY
    `)
    
    const counts = {}
    result.forEach(row => {
      counts[row.STUDY] = typeof row.count === 'bigint' ? Number(row.count) : row.count
    })
    studySampleCounts.value = counts
  } catch (err) {
    console.error('Failed to load study sample counts:', err)
  }
}

const getStudySampleCount = (study) => {
  return studySampleCounts.value[study] || 0
}

const filterStudies = () => {
  // This function is called on input change but the filtering is handled by the computed property
}

const toggleShowAllStudies = () => {
  showAllStudies.value = !showAllStudies.value
}

const selectAllStudies = () => {
  selectedStudies.value = [...availableStudies.value]
  updateChart()
}

const deselectAllStudies = () => {
  selectedStudies.value = []
  chartData.value = null
}

onMounted(async () => {
  await loadAvailableStudies()
  await loadStudySampleCounts()
  await updateChart()
})
</script>

<style scoped>
.timeline-chart {
  padding: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.chart-header h2 {
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  margin: 0;
}

.header-controls {
  display: flex;
  gap: 12px;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

.btn-primary {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.timeline-controls {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.controls-row {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 180px;
}

.control-group label {
  font-size: 13px;
  color: #475569;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.control-select {
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  color: #1e293b;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.control-select:hover {
  border-color: #cbd5e0;
}

.studies-section {
  border-top: 2px solid #e2e8f0;
  padding-top: 20px;
}

.studies-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.section-label {
  font-size: 16px;
  color: #1e293b;
  font-weight: 700;
  margin: 0;
}

.studies-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.study-search {
  position: relative;
  flex-grow: 1;
  max-width: 300px;
  min-width: 200px;
}

.selection-actions {
  display: flex;
  gap: 8px;
}

.btn-action {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-select-all {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.2);
}

.btn-select-all:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.btn-clear {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-clear:hover {
  background: #e2e8f0;
  color: #475569;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 16px;
}

.study-counter {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  background: #f1f5f9;
  padding: 8px 12px;
  border-radius: 6px;
  white-space: nowrap;
}

.study-filters-container {
  position: relative;
}

.study-filters {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  max-height: 240px;
  overflow: hidden;
  transition: max-height 0.3s ease;
}

.study-filters.expanded {
  max-height: none;
  overflow: visible;
}

.study-checkbox {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 8px;
}

.study-checkbox:hover {
  background: #f8fafc;
  border-color: #cbd5e0;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.study-checkbox input {
  margin: 0;
  width: 16px;
  height: 16px;
}

.study-name {
  font-weight: 600;
  font-size: 14px;
  flex-grow: 1;
}

.study-sample-count {
  font-size: 12px;
  color: #64748b;
  font-weight: 500;
}

.toggle-studies-btn {
  margin-top: 16px;
  padding: 10px 20px;
  background: #f8fafc;
  color: #475569;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.toggle-studies-btn:hover {
  background: #f1f5f9;
  border-color: #cbd5e0;
}

.filter-group {
  margin-bottom: 15px;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-group label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
  font-weight: 500;
  text-transform: uppercase;
}

.filter-group select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  min-width: 150px;
}

.filter-group button {
  margin-right: 10px;
}

.chart-container-wrapper {
  position: relative;
  height: 400px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #64748b;
  font-size: 16px;
}

.summary-stats {
  display: flex;
  gap: 30px;
  padding: 15px 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  color: #1e293b;
  font-weight: 700;
}

.btn-secondary {
  padding: 8px 16px;
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
}
</style>