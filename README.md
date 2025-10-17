# LabVantage Dashboard

A modern Vue 3 dashboard application for visualizing and analyzing laboratory sample data using DuckDB WASM for in-browser SQL querying.

## Overview

The LabVantage Dashboard provides an interactive web interface for exploring laboratory sample datasets with multiple visualization modes:

- **Overview Dashboard**: Key statistics and sample distributions
- **Timeline Chart**: Interactive timeline with study filtering and aggregation options
- **Sample Browser**: Searchable and filterable table view of sample data
- **Custom Query**: SQL query interface for advanced data exploration
- **Sample Matrix**: Tabular view showing sample counts by project and year

## Features

- 🚀 **Fast Performance**: Client-side data processing with DuckDB WASM
- 📊 **Interactive Charts**: Timeline visualizations with Chart.js
- 🔍 **Advanced Filtering**: Search, filter, and aggregate data in real-time
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🎨 **Professional UI**: Clean, presentation-ready interface
- 📈 **Multiple Views**: Different perspectives on the same dataset

## Technology Stack

- **Frontend**: Vue 3 with Composition API
- **Database**: DuckDB WASM for in-browser SQL processing
- **Charts**: Chart.js with vue-chartjs
- **Build Tool**: Vite
- **Data Format**: Parquet files for efficient storage and querying

## Prerequisites

- Node.js (version 16 or higher)
- npm or yarn package manager

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd i3h-labvantage-dashboard
```

2. Install dependencies:
```bash
npm install
```

## Data Preparation

### Converting CSV to Parquet

The dashboard expects data in Parquet format for optimal performance. If you have a CSV file, you can convert it using the included Python script:

1. **Install Python dependencies**:
   ```bash
   pip install pandas pyarrow
   ```

2. **Place your CSV file** in the `data/input/` directory. 

3. **Update the script** (if needed):
   
   Edit `convert_csv_to_parquet.py` and update the file paths:
   ```python
   csv_file = "data/input/your_file.csv"        # Update with your CSV filename
   parquet_file = "public/lv_export.parquet"  # Output location for web access
   ```

4. **Run the conversion script**:
   ```bash
   python convert_csv_to_parquet.py
   ```

   The script will:
   - Read your CSV file
   - Convert date columns (like VISITDATE) to proper datetime format
   - Save as compressed Parquet format in the `public/` directory
   - Display conversion progress and file information

5. **Verify the conversion**:
   The script will show you the first few rows and file statistics upon completion.

### Expected Data Schema

The dashboard expects a table with these columns:
- `STUDY`: Study identifier
- `PARTICIPANTID`: Participant identifier  
- `VISITDATE`: Visit date (YYYY-MM-DD format)
- `SAMPLETYPE`: Type of sample (e.g., 'CYTOF', 'PBMC', etc.)
- `SAMPLESTATUS`: Status of the sample
- Additional columns will be displayed in the Sample Browser

## Running the Application

### Development Server

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173/`

### Build for Production

Create a production build:
```bash
npm run build
```

### Preview Production Build

Preview the production build locally:
```bash
npm run preview
```

## Usage

### Dashboard Navigation

Use the tab navigation to switch between different views:

1. **Overview**: View key statistics and data distributions
2. **Timeline**: Analyze samples over time with filtering options
3. **Sample Browser**: Browse and search individual sample records
4. **Custom Query**: Write custom SQL queries against your data
5. **Sample Matrix**: View sample counts in a project/year matrix

### Timeline Chart Features

- **Study Filtering**: Search and select specific studies to visualize
- **Aggregation**: View data by day, week, or month
- **View Modes**: Switch between sample counts and cumulative totals
- **Interactive**: Hover for details, zoom and pan the chart

### Sample Matrix Features

- **Sample Type Selection**: Filter by any sample type in your dataset
- **Horizontal Scrolling**: Navigate through many years of data
- **Auto-scroll**: Automatically positions at the current year
- **Sample Counts**: Shows both individual cells and row/column totals

### Custom Queries

The Custom Query tab allows you to write SQL queries directly against your data:

```sql
-- Example: Find samples by study and date range
SELECT STUDY, COUNT(*) as sample_count 
FROM samples 
WHERE VISITDATE >= '2023-01-01' 
  AND VISITDATE <= '2023-12-31'
GROUP BY STUDY 
ORDER BY sample_count DESC;
```

## Configuration

### DuckDB Configuration

The DuckDB configuration is handled in `src/composables/useDuckDB.js`. The default setup:

- Loads the parquet file from `public/lv_export.parquet`
- Creates a table named `samples`
- Configures WASM bundle and worker files

### Vite Configuration

The `vite.config.js` file includes:

- DuckDB WASM optimizations
- CORS headers for local development
- Vue plugin configuration

## Project Structure

```
i3h-labvantage-dashboard/
├── data/
│   └── input/                 # Place CSV files here (contents ignored by git)
├── public/
│   └── lv_export.parquet      # Parquet data file (web accessible)
├── src/
│   ├── components/
│   │   ├── OverviewDashboard.vue
│   │   ├── TimelineChart.vue
│   │   ├── SampleBrowser.vue
│   │   ├── QueryBuilder.vue
│   │   └── CytofMatrix.vue
│   ├── composables/
│   │   └── useDuckDB.js       # DuckDB integration
│   ├── App.vue
│   └── main.js
├── convert_csv_to_parquet.py  # CSV to Parquet conversion script
├── package.json
├── vite.config.js
└── README.md
```

## Troubleshooting

### Common Issues

1. **"Failed to load parquet file"**
   - Ensure your parquet file is placed in `public/lv_export.parquet`
   - Check that the file was converted correctly using the Python conversion script
   - Update your application code to load from the new data folder structure

2. **Charts not displaying**
   - Verify your data has valid `VISITDATE` columns
   - Check browser console for JavaScript errors

3. **Performance issues**
   - Large datasets (>1M rows) may be slow in browser
   - Consider filtering data during the CSV to Parquet conversion

4. **CORS errors in development**
   - The Vite config should handle this automatically
   - Try clearing browser cache and restarting dev server
