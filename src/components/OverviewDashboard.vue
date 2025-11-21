<template>
  <div class="overview-dashboard">
    <h2>Dashboard Overview</h2>
    <assayAnalysis :executeQuery="executeQuery"></assayAnalysis>
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Samples</h3>
        <p class="stat-value">{{ stats.totalSamples }}</p>
      </div>

      <div class="stat-card">
        <h3>Unique Studies</h3>
        <p class="stat-value">{{ stats.uniqueStudies }}</p>
      </div>

      <div class="stat-card">
        <h3>Unique Participants</h3>
        <p class="stat-value">{{ stats.uniqueParticipants }}</p>
      </div>

      <div class="stat-card">
        <h3>Sample Types</h3>
        <p class="stat-value">{{ stats.sampleTypes }}</p>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-container">
        <h3>Samples by Status</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Count</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="status in statusDistribution" :key="status.status">
              <td>{{ status.status || "Unknown" }}</td>
              <td>{{ status.count }}</td>
              <td>{{ status.percentage }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="chart-container">
        <h3>Samples by Study</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Study</th>
              <th>Count</th>
              <th>Percentage</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="study in studyDistribution" :key="study.study">
              <td>{{ study.study }}</td>
              <td>{{ study.count }}</td>
              <td>{{ study.percentage }}%</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="chart-container">
        <h3>Top 10 Sample Types</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Sample Type</th>
              <th>Count</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="type in topSampleTypes" :key="type.sampletype">
              <td>{{ type.sampletype || "Unknown" }}</td>
              <td>{{ type.count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Study Classification Section -->
    <div class="classification-section">
      <h2>Study Classification</h2>

      <div class="charts-grid">
        <!-- Disease Classification Chart -->
        <div class="chart-card">
          <h3>Studies by Disease Classification</h3>
          <div class="bar-chart-container">
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
          <div class="bar-chart-container">
            <Bar
              v-if="therapyChartData"
              :data="therapyChartData"
              :options="therapyChartOptions"
            />
          </div>
        </div>
      </div>

      <!-- Therapy Stratification Chart -->
      <div class="chart-card-wide">
        <h3>Therapy Stratification</h3>
        <p class="chart-description">Distribution of therapy interventions across disease classifications</p>
        <div class="bar-chart-container-wide">
          <Bar
            v-if="combinedChartData"
            :data="combinedChartData"
            :options="combinedChartOptions"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import assayAnalysis from "./assayAnalysis.vue";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  executeQuery: Function,
});

const stats = ref({
  totalSamples: 0,
  uniqueStudies: 0,
  uniqueParticipants: 0,
  sampleTypes: 0,
});

const statusDistribution = ref([]);
const studyDistribution = ref([]);
const topSampleTypes = ref([]);

// Classification data
const diseaseChartData = ref(null);
const therapyChartData = ref(null);
const combinedChartData = ref(null);

// Color palettes
const diseaseColors = [
  '#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
  '#fa709a', '#feca57', '#ee5a6f', '#c44569', '#2c3e50',
];

const therapyColors = [
  '#38ef7d', '#11998e', '#667eea', '#f093fb', '#feca57',
  '#ee5a6f', '#4facfe', '#fa709a', '#c44569', '#43e97b',
];

const diseaseChartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => `Studies: ${context.parsed.x}`
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      title: { display: true, text: 'Number of Studies' }
    },
    y: {
      ticks: {
        autoSkip: false
      }
    }
  }
};

const therapyChartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      callbacks: {
        label: (context) => `Studies: ${context.parsed.x}`
      }
    }
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: { stepSize: 1 },
      title: { display: true, text: 'Number of Studies' }
    },
    y: {
      ticks: {
        autoSkip: false
      }
    }
  }
};

const combinedChartOptions = {
  indexAxis: 'y',
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: 'top'
    },
    title: { display: false },
    tooltip: {
      mode: 'index',
      intersect: false,
      callbacks: {
        label: (context) => `${context.dataset.label}: ${context.parsed.x} studies`
      }
    }
  },
  scales: {
    x: {
      stacked: true,
      beginAtZero: true,
      ticks: { stepSize: 1 },
      title: { display: true, text: 'Number of Studies' }
    },
    y: {
      stacked: true,
      ticks: {
        autoSkip: false
      }
    }
  }
};

const loadStats = async () => {
  try {
    const [totalResult, studiesResult, participantsResult, typesCountResult] =
      await Promise.all([
        props.executeQuery("SELECT COUNT(*) as count FROM samples"),
        props.executeQuery(
          "SELECT COUNT(DISTINCT STUDY) as count FROM samples"
        ),
        props.executeQuery(
          "SELECT COUNT(DISTINCT PARTICIPANTID) as count FROM samples"
        ),
        props.executeQuery(
          "SELECT COUNT(DISTINCT SAMPLETYPE) as count FROM samples"
        ),
      ]);

    stats.value.totalSamples = totalResult[0]?.count || 0;
    stats.value.uniqueStudies = studiesResult[0]?.count || 0;
    stats.value.uniqueParticipants = participantsResult[0]?.count || 0;
    stats.value.sampleTypes = typesCountResult[0]?.count || 0;

    const statusResult = await props.executeQuery(`
      SELECT 
        SAMPLESTATUS as status,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
      FROM samples
      GROUP BY SAMPLESTATUS
      ORDER BY count DESC
    `);
    statusDistribution.value = statusResult;

    const studyResult = await props.executeQuery(`
      SELECT 
        STUDY as study,
        COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
      FROM samples
      GROUP BY STUDY
      ORDER BY count DESC
    `);
    studyDistribution.value = studyResult;

    const sampleTypesResult = await props.executeQuery(`
      SELECT 
        SAMPLETYPE as sampletype,
        COUNT(*) as count
      FROM samples
      GROUP BY SAMPLETYPE
      ORDER BY count DESC
      LIMIT 10
    `);
    topSampleTypes.value = sampleTypesResult;
  } catch (err) {
    console.error("Failed to load stats:", err);
  }
};

const loadClassificationData = async () => {
  try {
    // Get study counts by disease
    const diseaseQuery = `
      SELECT
        "Disease classification" as disease,
        COUNT(DISTINCT STUDY) as study_count
      FROM samples
      WHERE "Disease classification" IS NOT NULL AND "Disease classification" != ''
      GROUP BY "Disease classification"
      ORDER BY study_count DESC
    `;
    const diseaseResult = await props.executeQuery(diseaseQuery);

    // Get study counts by therapy
    const therapyQuery = `
      SELECT
        "Ther Intervention classification" as therapy,
        COUNT(DISTINCT STUDY) as study_count
      FROM samples
      WHERE "Ther Intervention classification" IS NOT NULL AND "Ther Intervention classification" != ''
      GROUP BY "Ther Intervention classification"
      ORDER BY study_count DESC
    `;
    const therapyResult = await props.executeQuery(therapyQuery);

    // Process disease data for chart
    const diseaseLabels = diseaseResult.map(row => row.disease);
    const diseaseValues = diseaseResult.map(row => Number(row.study_count));

    diseaseChartData.value = {
      labels: diseaseLabels,
      datasets: [{
        label: 'Number of Studies',
        data: diseaseValues,
        backgroundColor: diseaseColors.slice(0, diseaseLabels.length),
        borderColor: diseaseColors.slice(0, diseaseLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    };

    // Process therapy data for chart
    const therapyLabels = therapyResult.map(row => row.therapy);
    const therapyValues = therapyResult.map(row => Number(row.study_count));

    therapyChartData.value = {
      labels: therapyLabels,
      datasets: [{
        label: 'Number of Studies',
        data: therapyValues,
        backgroundColor: therapyColors.slice(0, therapyLabels.length),
        borderColor: therapyColors.slice(0, therapyLabels.length).map(c => c + 'dd'),
        borderWidth: 1
      }]
    };

    // Create combined stacked horizontal bar chart
    // Query to get disease and therapy cross-tabulation
    const combinedQuery = `
      SELECT
        "Disease classification" as disease,
        "Ther Intervention classification" as therapy,
        COUNT(DISTINCT STUDY) as study_count
      FROM samples
      WHERE "Disease classification" IS NOT NULL AND "Disease classification" != ''
        AND "Ther Intervention classification" IS NOT NULL AND "Ther Intervention classification" != ''
      GROUP BY "Disease classification", "Ther Intervention classification"
      ORDER BY "Disease classification", study_count DESC
    `;
    const combinedResult = await props.executeQuery(combinedQuery);

    // Get unique therapies for datasets
    const uniqueTherapies = [...new Set(combinedResult.map(r => r.therapy))];
    const uniqueDiseases = [...new Set(combinedResult.map(r => r.disease))];

    // Create datasets for each therapy type
    const datasets = uniqueTherapies.map((therapy, idx) => {
      const data = uniqueDiseases.map(disease => {
        const record = combinedResult.find(
          r => r.disease === disease && r.therapy === therapy
        );
        return record ? Number(record.study_count) : 0;
      });

      return {
        label: therapy,
        data: data,
        backgroundColor: therapyColors[idx % therapyColors.length],
        borderColor: therapyColors[idx % therapyColors.length] + 'dd',
        borderWidth: 1
      };
    });

    combinedChartData.value = {
      labels: uniqueDiseases,
      datasets: datasets
    };

  } catch (err) {
    console.error('Error loading classification data:', err);
  }
};

onMounted(async () => {
  await loadStats();
  await loadClassificationData();
});
</script>

<style scoped>
.classification-section {
  margin-top: 40px;
  padding-top: 40px;
  border-top: 2px solid #e2e8f0;
}

.classification-section h2 {
  margin-bottom: 30px;
  color: #2c3e50;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 25px;
  margin-bottom: 25px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
}

.chart-card-wide {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  margin-bottom: 25px;
}

.chart-card h3,
.chart-card-wide h3 {
  margin-bottom: 8px;
  color: #34495e;
  font-size: 1.1em;
}

.chart-description {
  color: #64748b;
  font-size: 0.9em;
  margin-bottom: 15px;
  font-style: italic;
}

.bar-chart-container {
  margin-top: 20px;
  height: 400px;
}

.bar-chart-container-wide {
  margin-top: 20px;
  height: 500px;
}

.disease-name,
.therapy-name {
  font-weight: 500;
  color: #667eea;
}

@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .bar-chart-container {
    height: 350px;
  }

  .bar-chart-container-wide {
    height: 400px;
  }
}
</style>
