<template>
  <div class="assay-analysis">
    <h2>Assay Analysis</h2>
    <div class="chart-container">
      <h3>Assay Counts</h3>
      <!-- Sticky X-axis header -->
      <div class="x-axis-header">
        <Bar
          v-if="chartData"
          :data="emptyChartData"
          :options="xAxisOnlyOptions"
          :style="{ height: '50px' }"
        />
      </div>
      <!-- Chart body with fixed y-axis title -->
      <div class="chart-body">
        <!-- Fixed CyTOF label -->
        <div class="y-axis-title">CyTOF</div>
        <!-- Scrollable chart area -->
        <div class="chart-scroll-container">
          <div :style="{ height: chartHeight + 'px' }">
            <Bar
              v-if="chartData"
              :data="chartData"
              :options="chartOptionsNoXAxis"
            />
          </div>
        </div>
      </div>
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

const chartHeight = computed(() => {
  const numStudies = assayCounts.value.length;
  const heightPerStudy = 60; // pixels per study row
  const minHeight = 200;
  return Math.max(minHeight, numStudies * heightPerStudy);
});

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

// Empty chart data for the sticky x-axis header
const emptyChartData = computed(() => {
  if (assayCounts.value.length === 0) return null;

  // Find max value for consistent x-axis scale
  const maxVal = Math.max(
    ...assayCounts.value.map((a) =>
      Math.max(a.preProcess, a.postProcess, a.analysed)
    )
  );

  return {
    labels: [""],
    datasets: [
      {
        label: "Pre Process",
        data: [null],
        backgroundColor: "rgba(255, 159, 64, 0.7)",
      },
      {
        label: "Post Process",
        data: [null],
        backgroundColor: "rgba(75, 192, 192, 0.7)",
      },
      {
        label: "Analysed",
        data: [null],
        backgroundColor: "rgba(54, 162, 235, 0.7)",
      },
    ],
  };
});

// Compute max value for consistent scale
const maxValue = computed(() => {
  if (assayCounts.value.length === 0) return 100;
  return Math.max(
    ...assayCounts.value.map((a) =>
      Math.max(a.preProcess, a.postProcess, a.analysed)
    )
  );
});

// X-axis only options for the sticky header
const xAxisOnlyOptions = computed(() => ({
  indexAxis: "y",
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: true,
      position: "top",
      align: "center",
      labels: {
        font: {
          size: 16,
        },
        padding: 25,
        boxWidth: 20,
        boxHeight: 20,
      },
      padding: {
        bottom: 20,
      },
    },
    title: {
      display: false,
    },
    tooltip: {
      enabled: false,
    },
  },
  layout: {
    padding: {
      top: 10,
      bottom: 20,
    },
  },
  scales: {
    x: {
      position: "top",
      beginAtZero: true,
      max: maxValue.value * 1.1, // Add 10% padding
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
      display: false,
    },
  },
}));

// Main chart options without x-axis (shown in scrollable area)
const chartOptionsNoXAxis = computed(() => ({
  indexAxis: "y",
  responsive: true,
  maintainAspectRatio: false,
  barThickness: 12,
  categoryPercentage: 0.8,
  barPercentage: 0.9,
  plugins: {
    legend: {
      display: false, // Legend shown in header
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
      display: false, // Hide x-axis, shown in sticky header
      beginAtZero: true,
      max: maxValue.value * 1.1, // Same scale as header
    },
    y: {
      title: {
        display: false,
      },
      ticks: {
        font: {
          size: 14,
        },
      },
    },
  },
}));

const chartOptions = {
  indexAxis: "y", // This makes it a horizontal bar chart
  responsive: true,
  maintainAspectRatio: false,
  barThickness: 12, // Makes bars thinner
  categoryPercentage: 0.8, // Space for each category group
  barPercentage: 0.9, // Space for bars within category
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
        text: "CyTOF",
        font: {
          size: 20,
          weight: "bold",
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
    const assayColumns = sampleAssayMap["CyTOF"];
    const assayConditions = assayColumns
      .map((col) => `${col} = 'Y'`)
      .join(" OR ");

    // Get unique STUDY values that have CyTOF samples
    const studiesResult = await props.executeQuery(`
      SELECT DISTINCT STUDY
      FROM samples
      WHERE (${assayConditions})
        AND SAMPLETYPE = 'CyTOF'
        AND STUDY IS NOT NULL
      ORDER BY STUDY
    `);

    const studies = studiesResult.map((row) => row.STUDY);

    // For each study, calculate the 3 counts
    const countPromises = studies.map(async (study) => {
      const preProcessResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE CYTOFM = 'Y'
          AND SAMPLETYPE = 'CyTOF'
          AND LOCATION IS NOT NULL
          AND STUDY = '${study}'
      `);

      const postProcessResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE (${assayConditions})
          AND SAMPLETYPE = 'CyTOF'
          AND CYTOFPREPDATE IS NOT NULL
          AND STUDY = '${study}'
      `);

      const analysedResult = await props.executeQuery(`
        SELECT COUNT(*) as count
        FROM samples
        WHERE (${assayConditions})
          AND SAMPLETYPE = 'CyTOF'
          AND CYTOFTIER1ANALYSISDATE IS NOT NULL
          AND STUDY = '${study}'
      `);

      return {
        name: study,
        preProcess: Number(preProcessResult[0]?.count || 0),
        postProcess: Number(postProcessResult[0]?.count || 0),
        analysed: Number(analysedResult[0]?.count || 0),
      };
    });

    const results = await Promise.all(countPromises);
    // Only include studies with at least one non-zero count
    assayCounts.value = results.filter(
      (r) => r.preProcess > 0 || r.postProcess > 0 || r.analysed > 0
    );
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
}

.chart-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
}

.x-axis-header {
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
  height: 130px;
  border-bottom: 1px solid #eee;
}

.chart-body {
  display: flex;
  position: relative;
}

.y-axis-title {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-size: 20px;
  font-weight: bold;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  flex-shrink: 0;
}

.chart-scroll-container {
  max-height: 660px;
  overflow-y: auto;
  flex: 1;
}
</style>
