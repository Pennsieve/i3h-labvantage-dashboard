<template>
  <div class="study-classification">
    <h2>Study Classification by Disease and Therapy</h2>

    <div v-if="loading" class="loading">
      Loading classification data...
    </div>

    <div v-else-if="error" class="error">
      {{ error }}
    </div>

    <div v-else class="classification-container">
      <!-- Summary Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ totalStudies }}</div>
          <div class="stat-label">Total Studies</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ uniqueDiseases }}</div>
          <div class="stat-label">Disease Categories</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ uniqueTherapies }}</div>
          <div class="stat-label">Therapy Types</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalSamples.toLocaleString() }}</div>
          <div class="stat-label">Total Samples</div>
        </div>
      </div>

      <!-- Charts -->
      <div class="charts-grid">
        <!-- Disease Classification Chart -->
        <div class="chart-card">
          <h3>Studies by Disease Classification</h3>
          <div class="chart-container">
            <Bar
              v-if="diseaseChartData"
              :data="diseaseChartData"
              :options="diseaseChartOptions"
            />
          </div>
        </div>

        <!-- Therapy Classification Chart -->
        <div class="chart-card">
          <h3>Studies by Therapy Intervention</h3>
          <div class="chart-container">
            <Bar
              v-if="therapyChartData"
              :data="therapyChartData"
              :options="therapyChartOptions"
            />
          </div>
        </div>
      </div>

      <!-- Sample Count Charts -->
      <div class="charts-grid">
        <!-- Samples by Disease -->
        <div class="chart-card">
          <h3>Sample Counts by Disease Classification</h3>
          <div class="chart-container">
            <Bar
              v-if="diseaseSampleChartData"
              :data="diseaseSampleChartData"
              :options="diseaseSampleChartOptions"
            />
          </div>
        </div>

        <!-- Samples by Therapy -->
        <div class="chart-card">
          <h3>Sample Counts by Therapy Intervention</h3>
          <div class="chart-container">
            <Bar
              v-if="therapySampleChartData"
              :data="therapySampleChartData"
              :options="therapySampleChartOptions"
            />
          </div>
        </div>
      </div>

      <!-- Detailed Tables -->
      <div class="tables-container">
        <div class="table-card">
          <h3>Disease Classification Details</h3>
          <table>
            <thead>
              <tr>
                <th>Disease Category</th>
                <th>Number of Studies</th>
                <th>Sample Count</th>
                <th>Percentage of Samples</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in diseaseTable" :key="row.disease">
                <td class="disease-name">{{ row.disease || 'Unknown' }}</td>
                <td>{{ row.studyCount }}</td>
                <td>{{ row.sampleCount.toLocaleString() }}</td>
                <td>{{ row.percentage }}%</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="table-card">
          <h3>Therapy Intervention Details</h3>
          <table>
            <thead>
              <tr>
                <th>Therapy Type</th>
                <th>Number of Studies</th>
                <th>Sample Count</th>
                <th>Percentage of Samples</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in therapyTable" :key="row.therapy">
                <td class="therapy-name">{{ row.therapy || 'Unknown' }}</td>
                <td>{{ row.studyCount }}</td>
                <td>{{ row.sampleCount.toLocaleString() }}</td>
                <td>{{ row.percentage }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps({
  executeQuery: {
    type: Function,
    required: true
  }
})

const loading = ref(true)
const error = ref(null)
const totalStudies = ref(0)
const uniqueDiseases = ref(0)
const uniqueTherapies = ref(0)
const totalSamples = ref(0)

const diseaseChartData = ref(null)
const therapyChartData = ref(null)
const diseaseSampleChartData = ref(null)
const therapySampleChartData = ref(null)

const diseaseTable = ref([])
const therapyTable = ref([])

// Color palettes
const diseaseColors = [
  '#667eea', // Purple
  '#764ba2', // Deep purple
  '#f093fb', // Pink
  '#4facfe', // Blue
  '#43e97b', // Green
  '#fa709a', // Rose
  '#feca57', // Yellow
  '#ee5a6f', // Red
  '#c44569', // Dark pink
  '#2c3e50', // Dark blue
]

const therapyColors = [
  '#38ef7d', // Green
  '#11998e', // Teal
  '#667eea', // Purple
  '#f093fb', // Pink
  '#feca57', // Yellow
  '#ee5a6f', // Red
  '#4facfe', // Blue
  '#fa709a', // Rose
  '#c44569', // Dark pink
  '#43e97b', // Light green
]

const diseaseChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => `Studies: ${context.parsed.y}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      },
      title: {
        display: true,
        text: 'Number of Studies'
      }
    },
    x: {
      ticks: {
        autoSkip: false,
        maxRotation: 45,
        minRotation: 45
      }
    }
  }
}

const therapyChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => `Studies: ${context.parsed.y}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      },
      title: {
        display: true,
        text: 'Number of Studies'
      }
    },
    x: {
      ticks: {
        autoSkip: false,
        maxRotation: 45,
        minRotation: 45
      }
    }
  }
}

const diseaseSampleChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => `Samples: ${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Number of Samples'
      }
    },
    x: {
      ticks: {
        autoSkip: false,
        maxRotation: 45,
        minRotation: 45
      }
    }
  }
}

const therapySampleChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  aspectRatio: 2,
  plugins: {
    legend: {
      display: false
    },
    title: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => `Samples: ${context.parsed.y.toLocaleString()}`
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      title: {
        display: true,
        text: 'Number of Samples'
      }
    },
    x: {
      ticks: {
        autoSkip: false,
        maxRotation: 45,
        minRotation: 45
      }
    }
  }
}

const loadData = async () => {
  try {
    loading.value = true
    error.value = null

    // Get study counts by disease
    const diseaseQuery = `
      SELECT
        "Disease classification" as disease,
        COUNT(DISTINCT STUDY) as study_count
      FROM samples
      GROUP BY "Disease classification"
      ORDER BY study_count DESC
    `
    const diseaseResult = await props.executeQuery(diseaseQuery)

    // Get study counts by therapy
    const therapyQuery = `
      SELECT
        "Ther Intervention classification" as therapy,
        COUNT(DISTINCT STUDY) as study_count
      FROM samples
      GROUP BY "Ther Intervention classification"
      ORDER BY study_count DESC
    `
    const therapyResult = await props.executeQuery(therapyQuery)

    // Get sample counts by disease
    const diseaseSampleQuery = `
      SELECT
        "Disease classification" as disease,
        COUNT(*) as sample_count
      FROM samples
      GROUP BY "Disease classification"
      ORDER BY sample_count DESC
    `
    const diseaseSampleResult = await props.executeQuery(diseaseSampleQuery)

    // Get sample counts by therapy
    const therapySampleQuery = `
      SELECT
        "Ther Intervention classification" as therapy,
        COUNT(*) as sample_count
      FROM samples
      GROUP BY "Ther Intervention classification"
      ORDER BY sample_count DESC
    `
    const therapySampleResult = await props.executeQuery(therapySampleQuery)

    // Get total sample count
    const totalQuery = `SELECT COUNT(*) as total FROM samples`
    const totalResult = await props.executeQuery(totalQuery)
    totalSamples.value = Number(totalResult[0].total)

    // Process disease data for chart
    const diseaseLabels = diseaseResult.map(row => row.disease || 'Unknown')
    const diseaseValues = diseaseResult.map(row => Number(row.study_count))

    diseaseChartData.value = {
      labels: diseaseLabels,
      datasets: [{
        label: 'Number of Studies',
        data: diseaseValues,
        backgroundColor: diseaseColors.slice(0, diseaseLabels.length),
        borderColor: diseaseColors.slice(0, diseaseLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    }

    // Process therapy data for chart
    const therapyLabels = therapyResult.map(row => row.therapy || 'Unknown')
    const therapyValues = therapyResult.map(row => Number(row.study_count))

    therapyChartData.value = {
      labels: therapyLabels,
      datasets: [{
        label: 'Number of Studies',
        data: therapyValues,
        backgroundColor: therapyColors.slice(0, therapyLabels.length),
        borderColor: therapyColors.slice(0, therapyLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    }

    // Process disease sample data for chart
    const diseaseSampleLabels = diseaseSampleResult.map(row => row.disease || 'Unknown')
    const diseaseSampleValues = diseaseSampleResult.map(row => Number(row.sample_count))

    diseaseSampleChartData.value = {
      labels: diseaseSampleLabels,
      datasets: [{
        label: 'Number of Samples',
        data: diseaseSampleValues,
        backgroundColor: diseaseColors.slice(0, diseaseSampleLabels.length),
        borderColor: diseaseColors.slice(0, diseaseSampleLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    }

    // Process therapy sample data for chart
    const therapySampleLabels = therapySampleResult.map(row => row.therapy || 'Unknown')
    const therapySampleValues = therapySampleResult.map(row => Number(row.sample_count))

    therapySampleChartData.value = {
      labels: therapySampleLabels,
      datasets: [{
        label: 'Number of Samples',
        data: therapySampleValues,
        backgroundColor: therapyColors.slice(0, therapySampleLabels.length),
        borderColor: therapyColors.slice(0, therapySampleLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    }

    // Create disease table data
    diseaseTable.value = diseaseResult.map((row, idx) => {
      const sampleCount = Number(diseaseSampleResult[idx]?.sample_count || 0)
      return {
        disease: row.disease || 'Unknown',
        studyCount: Number(row.study_count),
        sampleCount: sampleCount,
        percentage: ((sampleCount / totalSamples.value) * 100).toFixed(1)
      }
    })

    // Create therapy table data
    therapyTable.value = therapyResult.map((row, idx) => {
      const sampleCount = Number(therapySampleResult[idx]?.sample_count || 0)
      return {
        therapy: row.therapy || 'Unknown',
        studyCount: Number(row.study_count),
        sampleCount: sampleCount,
        percentage: ((sampleCount / totalSamples.value) * 100).toFixed(1)
      }
    })

    // Update summary stats
    totalStudies.value = diseaseResult.reduce((sum, row) => sum + Number(row.study_count), 0)
    uniqueDiseases.value = diseaseResult.length
    uniqueTherapies.value = therapyResult.length

  } catch (err) {
    console.error('Error loading classification data:', err)
    error.value = 'Failed to load classification data: ' + err.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.study-classification {
  padding: 20px;
}

h2 {
  margin-bottom: 30px;
  color: #2c3e50;
}

h3 {
  margin-bottom: 20px;
  color: #34495e;
  font-size: 1.1em;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 1.1em;
}

.error {
  color: #e74c3c;
  background-color: #fdecea;
  border-radius: 8px;
  border: 1px solid #e74c3c;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 2.5em;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.95em;
  opacity: 0.95;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.chart-container {
  margin-top: 20px;
  height: 400px;
}

.tables-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 25px;
  margin-top: 30px;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

th {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

th:first-child {
  border-top-left-radius: 8px;
}

th:last-child {
  border-top-right-radius: 8px;
}

td {
  padding: 12px;
  border-bottom: 1px solid #e2e8f0;
  color: #2c3e50;
}

tr:last-child td {
  border-bottom: none;
}

tr:hover {
  background-color: #f8fafc;
}

.disease-name,
.therapy-name {
  font-weight: 500;
  color: #667eea;
}

@media (max-width: 768px) {
  .charts-grid,
  .tables-container {
    grid-template-columns: 1fr;
  }

  .chart-container {
    height: 300px;
  }
}
</style>
