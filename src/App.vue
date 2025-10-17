<template>
  <div id="app">
    <header>
      <h1>LabVantage Dashboard</h1>
    </header>
    
    <main v-if="!isLoading && !error">
      <div class="controls">
        <button @click="activeView = 'overview'" :class="{ active: activeView === 'overview' }">
          Overview
        </button>
        <button @click="activeView = 'timeline'" :class="{ active: activeView === 'timeline' }">
          Timeline
        </button>
        <button @click="activeView = 'samples'" :class="{ active: activeView === 'samples' }">
          Sample Browser
        </button>
        <button @click="activeView = 'query'" :class="{ active: activeView === 'query' }">
          Custom Query
        </button>
        <button @click="activeView = 'matrix'" :class="{ active: activeView === 'matrix' }">
          Sample Matrix
        </button>
      </div>

      <OverviewDashboard v-if="activeView === 'overview'" :executeQuery="executeQuery" />
      <TimelineChart v-if="activeView === 'timeline'" :executeQuery="executeQuery" />
      <SampleBrowser v-if="activeView === 'samples'" :executeQuery="executeQuery" />
      <QueryBuilder v-if="activeView === 'query'" :executeQuery="executeQuery" />
      <CytofMatrix v-if="activeView === 'matrix'" :executeQuery="executeQuery" />
    </main>
    
    <div v-else-if="isLoading" class="loading">
      <p>Loading DuckDB and data...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>Error: {{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useDuckDB } from './composables/useDuckDB'
import OverviewDashboard from './components/OverviewDashboard.vue'
import TimelineChart from './components/TimelineChart.vue'
import SampleBrowser from './components/SampleBrowser.vue'
import QueryBuilder from './components/QueryBuilder.vue'
import CytofMatrix from './components/CytofMatrix.vue'

const { isLoading, error, executeQuery } = useDuckDB()
const activeView = ref('overview')
</script>