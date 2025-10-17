<template>
  <div class="query-builder">
    <h2>Custom SQL Query</h2>
    
    <div class="query-section">
      <div class="query-examples">
        <h3>Example Queries:</h3>
        <button @click="setExampleQuery('participants')">Participants by Cohort</button>
        <button @click="setExampleQuery('timeline')">Sample Timeline</button>
        <button @click="setExampleQuery('disposal')">Disposal Analysis</button>
        <button @click="setExampleQuery('location')">Samples by Location</button>
      </div>
      
      <div class="query-input">
        <textarea
          v-model="queryText"
          placeholder="Enter your SQL query here..."
          @keydown.ctrl.enter="executeCustomQuery"
          @keydown.meta.enter="executeCustomQuery"
        ></textarea>
      </div>
      
      <div class="query-controls">
        <button @click="executeCustomQuery" class="btn-primary">
          Execute Query (Ctrl/Cmd + Enter)
        </button>
        <button @click="clearQuery" class="btn-secondary">
          Clear
        </button>
      </div>
    </div>
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="results.length > 0" class="results-section">
      <h3>Results ({{ results.length }} rows)</h3>
      <div class="table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th v-for="col in columns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in results" :key="idx">
              <td v-for="col in columns" :key="col">{{ row[col] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <button @click="exportResults" class="btn-export">
        Export to CSV
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  executeQuery: Function
})

const queryText = ref(`SELECT 
  STUDY,
  COUNT(*) as sample_count,
  COUNT(DISTINCT PARTICIPANTID) as participant_count
FROM samples
GROUP BY STUDY
ORDER BY sample_count DESC`)

const results = ref([])
const columns = ref([])
const error = ref('')

const exampleQueries = {
  participants: `SELECT 
  COHORT,
  COUNT(DISTINCT PARTICIPANTID) as participant_count,
  COUNT(*) as sample_count
FROM samples
GROUP BY COHORT
ORDER BY participant_count DESC`,
  
  timeline: `SELECT 
  DATE_TRUNC('month', VISITDATE::DATE) as month,
  COUNT(*) as sample_count,
  COUNT(DISTINCT PARTICIPANTID) as participants
FROM samples
WHERE VISITDATE IS NOT NULL
GROUP BY month
ORDER BY month DESC`,
  
  disposal: `SELECT 
  DISPOSALSTATUS,
  SAMPLESTATUS,
  COUNT(*) as count
FROM samples
GROUP BY DISPOSALSTATUS, SAMPLESTATUS
ORDER BY count DESC`,
  
  location: `SELECT 
  LOCATION,
  COUNT(*) as sample_count,
  COUNT(DISTINCT SAMPLETYPE) as sample_types
FROM samples
WHERE LOCATION IS NOT NULL AND LOCATION != ''
GROUP BY LOCATION
ORDER BY sample_count DESC
LIMIT 20`
}

const setExampleQuery = (type) => {
  queryText.value = exampleQueries[type]
}

const executeCustomQuery = async () => {
  error.value = ''
  results.value = []
  columns.value = []
  
  try {
    const result = await props.executeQuery(queryText.value)
    results.value = result
    
    if (result.length > 0) {
      columns.value = Object.keys(result[0])
    }
  } catch (err) {
    error.value = `Query error: ${err.message}`
  }
}

const clearQuery = () => {
  queryText.value = ''
  results.value = []
  columns.value = []
  error.value = ''
}

const exportResults = () => {
  if (results.value.length === 0) return
  
  const csvContent = [
    columns.value.join(','),
    ...results.value.map(row => 
      columns.value.map(col => {
        const value = row[col]
        return typeof value === 'string' && value.includes(',') 
          ? `"${value}"` 
          : value
      }).join(',')
    )
  ].join('\n')
  
  const blob = new Blob([csvContent], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'query_results.csv'
  link.click()
  URL.revokeObjectURL(url)
}
</script>