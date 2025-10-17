import { ref, onMounted } from 'vue'
import * as duckdb from '@duckdb/duckdb-wasm'

export function useDuckDB() {
  const db = ref(null)
  const conn = ref(null)
  const isLoading = ref(true)
  const error = ref(null)

  const initDuckDB = async () => {
    try {
      isLoading.value = true
      
      const MANUAL_BUNDLES = {
        mvp: {
          mainModule: '/node_modules/@duckdb/duckdb-wasm/dist/duckdb-mvp.wasm',
          mainWorker: '/node_modules/@duckdb/duckdb-wasm/dist/duckdb-browser-mvp.worker.js',
        },
        eh: {
          mainModule: '/node_modules/@duckdb/duckdb-wasm/dist/duckdb-eh.wasm',
          mainWorker: '/node_modules/@duckdb/duckdb-wasm/dist/duckdb-browser-eh.worker.js',
        },
      }
      
      const bundle = await duckdb.selectBundle(MANUAL_BUNDLES)
      
      const worker = new Worker(bundle.mainWorker)
      const logger = new duckdb.ConsoleLogger()
      
      db.value = new duckdb.AsyncDuckDB(logger, worker)
      await db.value.instantiate(bundle.mainModule)
      
      conn.value = await db.value.connect()
      
      const parquetResponse = await fetch('/lv_export.parquet')
      const parquetBuffer = await parquetResponse.arrayBuffer()
      
      await db.value.registerFileBuffer('lv_export.parquet', new Uint8Array(parquetBuffer))
      
      await conn.value.query(`
        CREATE OR REPLACE VIEW samples AS 
        SELECT * FROM read_parquet('lv_export.parquet')
      `)
      
      isLoading.value = false
    } catch (err) {
      console.error('Failed to initialize DuckDB:', err)
      error.value = err.message
      isLoading.value = false
    }
  }

  const executeQuery = async (sql) => {
    if (!conn.value) {
      throw new Error('Database connection not initialized')
    }
    
    try {
      const result = await conn.value.query(sql)
      return result.toArray().map(row => row.toJSON())
    } catch (err) {
      console.error('Query error:', err)
      throw err
    }
  }

  onMounted(() => {
    initDuckDB()
  })

  return {
    db,
    conn,
    isLoading,
    error,
    executeQuery
  }
}