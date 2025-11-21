<template>
  <div class="assays-view">
    <h2>Assay Analysis</h2>
    <assayAnalysis :executeQuery="executeQuery"></assayAnalysis>
  </div>
</template>

<script setup>
import assayAnalysis from "./assayAnalysis.vue";

const props = defineProps({
  executeQuery: Function,
});
</script>

<style scoped>
.assays-view {
  padding: 20px;
}

h2 {
  margin-bottom: 30px;
  color: #2c3e50;
}
</style>
