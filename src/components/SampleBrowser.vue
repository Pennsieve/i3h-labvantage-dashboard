<template>
  <div class="sample-browser">
    <h2>Sample Browser</h2>
    
    <div class="filters">
      <div class="filter-group">
        <label>Study:</label>
        <select v-model="filters.study" @change="loadSamples">
          <option value="">All Studies</option>
          <option v-for="study in studyOptions" :key="study" :value="study">{{ study }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Status:</label>
        <select v-model="filters.status" @change="loadSamples">
          <option value="">All Statuses</option>
          <option v-for="status in statusOptions" :key="status" :value="status">{{ status }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Sample Type:</label>
        <select v-model="filters.sampleType" @change="loadSamples">
          <option value="">All Types</option>
          <option v-for="type in typeOptions" :key="type" :value="type">{{ type }}</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Search Sample ID:</label>
        <input 
          v-model="filters.searchId" 
          @input="loadSamples"
          placeholder="Enter sample ID..."
        />
      </div>
    </div>
    
    <div class="results-info">
      Showing {{ samples.length }} samples
    </div>
    
    <div class="table-container">
      <table class="samples-table">
        <thead>
          <tr>
            <th>Sample ID</th>
            <th>Study</th>
            <th>Participant</th>
            <th>Visit</th>
            <th>Visit Date</th>
            <th>Sample Type</th>
            <th>Status</th>
            <th>Location</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sample in samples" :key="sample.SAMPLEID">
            <td>{{ sample.SAMPLEID }}</td>
            <td>{{ sample.STUDY }}</td>
            <td>{{ sample.PARTICIPANTID }}</td>
            <td>{{ sample.VISIT }}</td>
            <td>{{ formatDate(sample.VISITDATE) }}</td>
            <td>{{ sample.SAMPLETYPE }}</td>
            <td>
              <span :class="getStatusClass(sample.SAMPLESTATUS)">
                {{ sample.SAMPLESTATUS }}
              </span>
            </td>
            <td>{{ sample.LOCATION }}</td>
            <td>{{ sample.QUANTITY }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  executeQuery: Function
})

const samples = ref([])
const studyOptions = ref([])
const statusOptions = ref([])
const typeOptions = ref([])

const filters = ref({
  study: '',
  status: '',
  sampleType: '',
  searchId: ''
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString()
}

const getStatusClass = (status) => {
  const statusLower = status?.toLowerCase() || ''
  if (statusLower.includes('disposed')) return 'status-disposed'
  if (statusLower.includes('circulation')) return 'status-active'
  if (statusLower.includes('prep')) return 'status-prep'
  return 'status-default'
}

const loadFilterOptions = async () => {
  try {
    const [studies, statuses, types] = await Promise.all([
      props.executeQuery('SELECT DISTINCT STUDY FROM samples WHERE STUDY IS NOT NULL ORDER BY STUDY'),
      props.executeQuery('SELECT DISTINCT SAMPLESTATUS FROM samples WHERE SAMPLESTATUS IS NOT NULL ORDER BY SAMPLESTATUS'),
      props.executeQuery('SELECT DISTINCT SAMPLETYPE FROM samples WHERE SAMPLETYPE IS NOT NULL ORDER BY SAMPLETYPE')
    ])
    
    studyOptions.value = studies.map(s => s.STUDY)
    statusOptions.value = statuses.map(s => s.SAMPLESTATUS)
    typeOptions.value = types.map(t => t.SAMPLETYPE)
  } catch (err) {
    console.error('Failed to load filter options:', err)
  }
}

const loadSamples = async () => {
  try {
    let whereConditions = []
    
    if (filters.value.study) {
      whereConditions.push(`STUDY = '${filters.value.study}'`)
    }
    if (filters.value.status) {
      whereConditions.push(`SAMPLESTATUS = '${filters.value.status}'`)
    }
    if (filters.value.sampleType) {
      whereConditions.push(`SAMPLETYPE = '${filters.value.sampleType}'`)
    }
    if (filters.value.searchId) {
      whereConditions.push(`SAMPLEID LIKE '%${filters.value.searchId}%'`)
    }
    
    const whereClause = whereConditions.length > 0 
      ? `WHERE ${whereConditions.join(' AND ')}`
      : ''
    
    const query = `
      SELECT * FROM samples
      ${whereClause}
      ORDER BY VISITDATE DESC, SAMPLEID
      LIMIT 100
    `
    
    const result = await props.executeQuery(query)
    samples.value = result
  } catch (err) {
    console.error('Failed to load samples:', err)
  }
}

onMounted(async () => {
  await loadFilterOptions()
  await loadSamples()
})
</script>