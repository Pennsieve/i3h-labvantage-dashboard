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
  barThickness: 60, // Makes bars thinner
  plugins: {
    legend: {
      display: true,
      position: "top",
      labels: {
        font: {
          size: 24,
        },
      },
    },
    title: {
      display: false,
    },
    tooltip: {
      bodyFont: {
        size: 14,
      },
      titleFont: {
        size: 16,
      },
    },
  },
  scales: {
    x: {
      beginAtZero: true,
      title: {
        display: true,
        text: "Count",
        font: {
          size: 16,
        },
      },
      ticks: {
        font: {
          size: 14,
        },
      },
    },
    y: {
      title: {
        display: true,
        text: "Assay Name",
        font: {
          size: 16,
        },
      },
      ticks: {
        font: {
          size: 14,
        },
      },
    },
  },
};

const loadAssayData = async () => {
  try {
    // Get unique sample types from the map
    const sampleTypes = Object.keys(sampleAssayMap);

    const countPromises = sampleTypes.map(async (sampleType) => {
      const assayColumns = sampleAssayMap[sampleType];

      // Build OR conditions for all assay columns
      const assayConditions = assayColumns
        .map((col) => `${col} = 'Y'`)
        .join(" OR ");

      const preProcessResult = await props.executeQuery(`
      SELECT COUNT(*) as count
      FROM samples
      WHERE CYTOFM = 'Y' 
        AND SAMPLETYPE = 'CyTOF'
        AND LOCATION NOT NULL
      `);

      const postProcessResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE (${assayConditions})
          AND SAMPLETYPE = '${sampleType}'
          AND CYTOFPREPDATE IS NOT NULL
      `);

      const analysedResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE (${assayConditions})
          AND SAMPLETYPE = '${sampleType}'
          AND CYTOFTIER1ANALYSISDATE IS NOT NULL
      `);

      return {
        name: sampleType,
        preProcess: Number(preProcessResult[0]?.count || 0),
        postProcess: Number(postProcessResult[0]?.count || 0),
        analysed: Number(analysedResult[0]?.count || 0),
      };
    });

    const results = await Promise.all(countPromises);
    assayCounts.value = results;
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
