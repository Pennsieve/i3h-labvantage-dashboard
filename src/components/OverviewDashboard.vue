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
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import assayAnalysis from "./assayAnalysis.vue";
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

onMounted(() => {
  loadStats();
});
</script>
