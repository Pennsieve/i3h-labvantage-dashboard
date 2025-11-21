<template>
  <div class="assay-analysis">
    <h2>Assay Analysis</h2>
    <div class="chart-container">
      <h3>Assay Counts</h3>
      <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { Bar } from "vue-chartjs";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import modelConfig from "../config/model.json";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const props = defineProps({
  executeQuery: Function,
});

const sampleAssayMap = {
  CyTOF: ["CYTOFM", "CYTOFTIER1"],
};
const assayCounts = ref([]);

const chartData = computed(() => {
  if (assayCounts.value.length === 0) return null;

  return {
    labels: assayCounts.value.map((assay) => assay.name),
    datasets: [
      {
        label: "Pre Process",
        data: assayCounts.value.map((assay) => assay.preProcess),
        backgroundColor: "rgba(255, 159, 64, 0.7)",
        borderColor: "rgba(255, 159, 64, 1)",
        borderWidth: 1,
      },
      {
        label: "Post Process",
        data: assayCounts.value.map((assay) => assay.postProcess),
        backgroundColor: "rgba(75, 192, 192, 0.7)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
      {
        label: "Analysed",
        data: assayCounts.value.map((assay) => assay.analysed),
        backgroundColor: "rgba(54, 162, 235, 0.7)",
        borderColor: "rgba(54, 162, 235, 1)",
        borderWidth: 1,
      },
    ],
  };
});

const chartOptions = {
  indexAxis: "y", // This makes it a horizontal bar chart
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "top",
    },
    title: {
      display: false,
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      title: {
        display: true,
        text: "Count",
      },
    },
    y: {
      title: {
        display: true,
        text: "Assay Name",
      },
    },
  },
};

const loadAssayData = async () => {
  try {
    // Parse model.json to find all columns with category = "assay"
    const assayColumns = Object.entries(modelConfig.columns)
      .filter(([_, config]) => config.category === "assay")
      .map(([columnName, config]) => config.name || columnName);

    // Query count for each assay (Pre Process, Post Process, and Analysed)
    const countPromises = assayColumns.map(async (columnName) => {
      const analysisDateColumn = `${columnName}AnalysisDate`;

      // Find which sample types include this assay
      const validSampleTypes = Object.entries(sampleAssayMap)
        .filter(([_, assays]) => assays.includes(columnName))
        .map(([sampleType, _]) => sampleType);
      console.log(validSampleTypes);
      // Skip this assay if it's not in any sample type's valid list
      if (validSampleTypes.length === 0) {
        return null;
      }

      // Build the SAMPLETYPE filter
      const sampleTypeFilter = validSampleTypes
        .map((st) => `'${st}'`)
        .join(", ");

      const preProcessResult = await props.executeQuery(`
      SELECT COUNT(*) as count
      FROM samples
      WHERE ${columnName} = 'Y' 
        AND SAMPLETYPE IN (${sampleTypeFilter})
        AND DISPOSALSTATUS != 'Not Collected'
    `);

      const postProcessResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE ${columnName} = 'Y' AND SAMPLETYPE IN (${sampleTypeFilter})
      `);

      const analysedResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE ${columnName} = 'Y' AND ${analysisDateColumn} IS NOT NULL AND SAMPLETYPE IN (${sampleTypeFilter})
      `);

      return {
        name: columnName,
        preProcess: Number(preProcessResult[0]?.count || 0),
        postProcess: Number(postProcessResult[0]?.count || 0),
        analysed: Number(analysedResult[0]?.count || 0),
      };
    });

    const results = await Promise.all(countPromises);

    // Filter out null results (assays not in sampleAssayMap)
    assayCounts.value = results.filter((result) => result !== null);
  } catch (err) {
    console.error("Failed to load assay data:", err);
  }
};

onMounted(() => {
  loadAssayData();
});
</script>

<style scoped>
.assay-analysis {
  padding: 20px;
}

.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
  height: 600px;
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}
</style>
