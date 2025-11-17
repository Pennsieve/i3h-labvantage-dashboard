<template>
  <div class="cytof-matrix">
    <div class="header-section">
      <h2>Sample Collection Matrix</h2>
      <p class="subtitle">Project overview showing samples collected by year</p>
      
      <div class="controls-section">
        <div class="filter-group">
          <label for="sampleType">Sample Type:</label>
          <select id="sampleType" v-model="selectedSampleType" @change="async () => { await loadMatrixData(); await scrollToCurrentYear(); }">
            <option value="">All Sample Types</option>
            <option v-for="type in availableSampleTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading sample data...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
    </div>
    
    <div v-else class="matrix-container">
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">🔬</div>
          <div class="card-content">
            <h3>{{ selectedSampleType ? selectedSampleType + ' Samples' : 'Total Samples' }}</h3>
            <p class="card-value">{{ totalSamples.toLocaleString() }}</p>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="card-icon">📊</div>
          <div class="card-content">
            <h3>Active Projects</h3>
            <p class="card-value">{{ projectsData.length }}</p>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="card-icon">📅</div>
          <div class="card-content">
            <h3>Years of Data</h3>
            <p class="card-value">{{ availableYears.length }}</p>
          </div>
        </div>
      </div>
      
      <div class="table-wrapper" ref="tableWrapper">
        <table class="cytof-table">
          <thead>
            <tr>
              <th class="project-header">Project</th>
              <th class="year-header">Pre 2018</th>
              <th v-for="year in availableYears" :key="year" class="year-header">
                {{ year }}
              </th>
              <th class="total-header">Total</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="project in projectsData" :key="project.study" class="project-row">
              <td class="project-cell">
                <div class="project-info">
                  <span class="project-name">{{ project.study }}</span>
                  <span class="project-samples">{{ project.total.toLocaleString() }} samples</span>
                </div>
              </td>
              <td class="data-cell">
                <div class="sample-count" :class="getCellClass(project.pre2018Total || 0)">
                  <span class="count-number">{{ (project.pre2018Total || 0).toLocaleString() }}</span>
                  <div class="count-bar" :style="{ width: getBarWidth(project.pre2018Total || 0) + '%' }"></div>
                </div>
              </td>
              <td v-for="year in availableYears" :key="year" class="data-cell">
                <div class="sample-count" :class="getCellClass(project.yearData[year] || 0)">
                  <span class="count-number">{{ (project.yearData[year] || 0).toLocaleString() }}</span>
                  <div class="count-bar" :style="{ width: getBarWidth(project.yearData[year] || 0) + '%' }"></div>
                </div>
              </td>
              <td class="total-cell">
                <div class="total-count">
                  {{ project.total.toLocaleString() }}
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="totals-row">
              <td class="totals-label">
                <strong>Year Totals</strong>
              </td>
              <td class="year-total">
                <strong>{{ getPre2018Total().toLocaleString() }}</strong>
              </td>
              <td v-for="year in availableYears" :key="year" class="year-total">
                <strong>{{ getYearTotal(year).toLocaleString() }}</strong>
              </td>
              <td class="grand-total">
                <strong>{{ totalSamples.toLocaleString() }}</strong>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <div class="legend">
        <h4>Sample Count Legend</h4>
        <div class="legend-items">
          <div class="legend-item">
            <div class="legend-color low"></div>
            <span>1-99 samples</span>
          </div>
          <div class="legend-item">
            <div class="legend-color medium"></div>
            <span>100-499 samples</span>
          </div>
          <div class="legend-item">
            <div class="legend-color high"></div>
            <span>500+ samples</span>
          </div>
          <div class="legend-item">
            <div class="legend-color none"></div>
            <span>No samples</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick } from 'vue'

const props = defineProps({
  executeQuery: Function
})

const isLoading = ref(true)
const error = ref('')
const projectsData = ref([])
const availableYears = ref([])
const availableSampleTypes = ref([])
const selectedSampleType = ref('')
const totalSamples = ref(0)
const maxSampleCount = ref(0)
const tableWrapper = ref(null)

const loadSampleTypes = async () => {
  try {
    const query = `
      SELECT DISTINCT SAMPLETYPE 
      FROM samples 
      WHERE SAMPLETYPE IS NOT NULL 
      ORDER BY SAMPLETYPE
    `
    
    const result = await props.executeQuery(query)
    availableSampleTypes.value = result.map(r => r.SAMPLETYPE)
    console.log('Available sample types:', availableSampleTypes.value)
  } catch (err) {
    console.error('Failed to load sample types:', err)
  }
}

const loadMatrixData = async () => {
  try {
    isLoading.value = true
    error.value = ''
    
    // Build WHERE clause based on selected sample type
    let whereClause = 'WHERE VISITDATE IS NOT NULL AND STUDY IS NOT NULL'
    if (selectedSampleType.value) {
      whereClause += ` AND SAMPLETYPE ILIKE '%${selectedSampleType.value}%'`
    }
    
    // Query for samples by project and year
    const query = `
      SELECT 
        STUDY as project,
        EXTRACT(YEAR FROM VISITDATE::DATE) as year,
        COUNT(*) as sample_count
      FROM samples
      ${whereClause}
      GROUP BY STUDY, EXTRACT(YEAR FROM VISITDATE::DATE)
      ORDER BY STUDY, year
    `
    
    console.log('Executing matrix query:', query)
    const result = await props.executeQuery(query)
    console.log('Matrix query result:', result)
    
    if (!result || result.length === 0) {
      const sampleTypeText = selectedSampleType.value || 'all'
      error.value = `No ${sampleTypeText} samples found in the database`
      return
    }
    
    // Get all unique years and sort them
    const years = [...new Set(result.map(row => {
      const year = typeof row.year === 'bigint' ? Number(row.year) : row.year
      return Number(year)
    }))].sort()

    // Filter to only include years 2018 and later
    availableYears.value = years.filter(year => year >= 2018)

    // Group data by project
    const projectMap = new Map()
    let total = 0
    let maxCount = 0

    result.forEach(row => {
      const project = row.project
      const year = typeof row.year === 'bigint' ? Number(row.year) : Number(row.year)
      const count = typeof row.sample_count === 'bigint' ? Number(row.sample_count) : row.sample_count

      if (!projectMap.has(project)) {
        projectMap.set(project, {
          study: project,
          yearData: {},
          pre2018Total: 0,
          total: 0
        })
      }

      // If year is before 2018, add to pre2018Total
      if (year < 2018) {
        projectMap.get(project).pre2018Total += count
      } else {
        // Otherwise, add to yearData
        projectMap.get(project).yearData[year] = count
        maxCount = Math.max(maxCount, count)
      }

      projectMap.get(project).total += count
      total += count
    })

    // Calculate maxCount including pre2018Total aggregates
    projectMap.forEach(project => {
      if (project.pre2018Total > 0) {
        maxCount = Math.max(maxCount, project.pre2018Total)
      }
    })
    
    // Convert to array and sort by total descending
    projectsData.value = Array.from(projectMap.values())
      .sort((a, b) => b.total - a.total)
    
    totalSamples.value = total
    maxSampleCount.value = maxCount
    
    console.log('Processed data:', {
      projects: projectsData.value,
      years: availableYears.value,
      total: totalSamples.value
    })
    
  } catch (err) {
    console.error('Failed to load matrix data:', err)
    error.value = `Failed to load data: ${err.message}`
  } finally {
    isLoading.value = false
  }
}

const getPre2018Total = () => {
  return projectsData.value.reduce((sum, project) => {
    return sum + (project.pre2018Total || 0)
  }, 0)
}

const getYearTotal = (year) => {
  return projectsData.value.reduce((sum, project) => {
    return sum + (project.yearData[year] || 0)
  }, 0)
}

const getCellClass = (count) => {
  if (count === 0) return 'count-none'
  if (count < 100) return 'count-low'
  if (count < 500) return 'count-medium'
  return 'count-high'
}

const getBarWidth = (count) => {
  if (maxSampleCount.value === 0) return 0
  return Math.min((count / maxSampleCount.value) * 100, 100)
}

const scrollToCurrentYear = async () => {
  await nextTick()
  
  if (!tableWrapper.value || availableYears.value.length === 0) return
  
  const currentYear = new Date().getFullYear()
  const closestYear = availableYears.value.reduce((closest, year) => {
    return Math.abs(year - currentYear) < Math.abs(closest - currentYear) ? year : closest
  })
  
  // Calculate the position to scroll to show the current/closest year
  const projectColumnWidth = 200 // min-width of project header
  const yearColumnWidth = 100 // min-width of year columns
  const yearIndex = availableYears.value.indexOf(closestYear)
  
  if (yearIndex >= 0) {
    // Scroll to show the current year, but leave some padding to see a few years before it
    const targetScrollPosition = Math.max(0, 
      projectColumnWidth + (yearIndex - 2) * yearColumnWidth
    )
    
    tableWrapper.value.scrollLeft = targetScrollPosition
    console.log(`Scrolled to year ${closestYear} at position ${targetScrollPosition}`)
  }
}

onMounted(async () => {
  await loadSampleTypes()
  await loadMatrixData()
  await scrollToCurrentYear()
})
</script>

<style scoped>
.cytof-matrix {
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;
}

.header-section {
  text-align: center;
  margin-bottom: 30px;
}

.header-section h2 {
  color: #1e293b;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
}

.subtitle {
  color: #64748b;
  font-size: 16px;
  margin: 0 0 20px 0;
}

.controls-section {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.filter-group select {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  color: #1e293b;
  font-weight: 500;
  min-width: 180px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-group select:hover {
  border-color: #667eea;
}

.loading-state, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.summary-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid #e2e8f0;
}

.card-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
}

.card-content h3 {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 4px 0;
  font-weight: 500;
}

.card-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.table-wrapper {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  overflow-x: auto;
  overflow-y: hidden;
  margin-bottom: 30px;
  max-width: 100%;
}

.cytof-table {
  width: 100%;
  border-collapse: collapse;
}

.cytof-table thead tr {
  background: linear-gradient(135deg, #667eea, #764ba2);
}

.cytof-table th {
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: white;
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.project-header {
  min-width: 200px;
  position: sticky;
  left: 0;
  background: linear-gradient(135deg, #667eea, #764ba2);
  z-index: 10;
}

.year-header, .total-header {
  text-align: center;
  min-width: 100px;
}

.project-row {
  border-bottom: 1px solid #f1f5f9;
  transition: background-color 0.2s;
}

.project-row:hover {
  background: #f8fafc;
}

.project-cell {
  padding: 16px 12px;
  background: white;
  position: sticky;
  left: 0;
  z-index: 5;
  border-right: 2px solid #e2e8f0;
}

.project-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.project-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
}

.project-samples {
  font-size: 12px;
  color: #64748b;
}

.data-cell {
  padding: 12px;
  text-align: center;
  position: relative;
}

.sample-count {
  position: relative;
  padding: 8px 12px;
  border-radius: 6px;
  min-height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.count-number {
  position: relative;
  z-index: 2;
  font-weight: 600;
  font-size: 13px;
}

.count-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  border-radius: 6px;
  opacity: 0.3;
  transition: width 0.3s ease;
}

.count-none {
  background: #f8fafc;
  color: #94a3b8;
}

.count-none .count-bar {
  background: #e2e8f0;
}

.count-low {
  background: #fef3c7;
  color: #92400e;
}

.count-low .count-bar {
  background: #fbbf24;
}

.count-medium {
  background: #dbeafe;
  color: #1e40af;
}

.count-medium .count-bar {
  background: #3b82f6;
}

.count-high {
  background: #dcfce7;
  color: #166534;
}

.count-high .count-bar {
  background: #22c55e;
}

.total-cell {
  padding: 16px 12px;
  text-align: center;
  background: #f8fafc;
  border-left: 2px solid #e2e8f0;
}

.total-count {
  font-weight: 700;
  color: #1e293b;
  font-size: 16px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea20, #764ba220);
  border-radius: 6px;
}

.totals-row {
  background: #f8fafc;
  border-top: 2px solid #e2e8f0;
}

.totals-row td {
  padding: 16px 12px;
  text-align: center;
  font-size: 14px;
  color: #1e293b;
}

.totals-label {
  text-align: left !important;
  background: white;
  position: sticky;
  left: 0;
  z-index: 5;
  border-right: 2px solid #e2e8f0;
}

.grand-total {
  background: linear-gradient(135deg, #667eea20, #764ba220);
  border-left: 2px solid #e2e8f0;
}

.legend {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.legend h4 {
  color: #1e293b;
  font-size: 16px;
  margin-bottom: 12px;
}

.legend-items {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #64748b;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.none {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.legend-color.low {
  background: #fef3c7;
}

.legend-color.medium {
  background: #dbeafe;
}

.legend-color.high {
  background: #dcfce7;
}

@media (max-width: 768px) {
  .cytof-table {
    font-size: 12px;
  }
  
  .cytof-table th,
  .cytof-table td {
    padding: 8px 6px;
  }
  
  .summary-cards {
    grid-template-columns: 1fr;
  }
}
</style>