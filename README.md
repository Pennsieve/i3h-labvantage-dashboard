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

### Install Node.js and npm

1. **Install nvm (Node Version Manager)**

   - macOS/Linux: Follow instructions at https://github.com/nvm-sh/nvm
   - Windows: Use nvm-windows from https://github.com/coreybutler/nvm-windows

2. **Install Node.js** (this also installs npm automatically)

```bash
   nvm install 18
   nvm use 18
```

3. **Verify installation**

```bash
   node --version
   npm --version
```

You should see version numbers for both commands.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Pennsieve/i3h-labvantage-dashboard.git
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

   First, verify pip is installed:

```bash
   pip --version
```

If pip is not installed, see the [pip installation guide](https://pip.pypa.io/en/stable/installation/).

Then install the required packages:

```bash
   pip install pandas
   pip install pyarrow
```

**Note**: If `pip` command is not recognized, try using `python -m pip install` instead:

```bash
   python -m pip install pandas
   python -m pip install pyarrow
```

2. **Place your CSV file(s)** in the `data/` directory.

3. **Update the config** (if needed):

   Edit `data/config/model.json` to configure your data processing:

```json
{
  "file_names": ["your_file.csv", "optional_second_file.csv"],
  "column_mapping": {
    "old_column_name": "new_column_name"
  },
  "join": {
    "type": "left",
    "column": "STUDY"
  },
  "columns": {
    "VISITDATE": { "type": "datetime" },
    "IRB": { "type": "array_of_strings", "delimiter": " and " }
  },
  "default_type": "string"
}
```

- **file_names**: List your CSV files (they should be in the `data/` folder)

- **column_mapping** (optional): Rename columns to match dashboard requirements

```json
     "column_mapping": {
       "assay_study": "STUDY",
       "patient_id": "PARTICIPANTID",
       "visit_dt": "VISITDATE"
     }
```

     The dashboard expects these column names:
     - `STUDY`: Study identifier
     - `PARTICIPANTID`: Participant identifier
     - `VISITDATE`: Visit date
     - `SAMPLETYPE`: Type of sample
     - `SAMPLESTATUS`: Status of the sample

     If your CSV has different column names, use `column_mapping` to rename them.

- **join**: If you have multiple CSV files, specify how to join them

  - `type`: "left" keeps all rows from first file, "inner" only keeps matching rows
  - `column`: Which column to join on (e.g., "STUDY", "SAMPLEID")

- **columns**: Specify data types for specific columns

  - `datetime`: For date columns
  - `array_of_strings`: For columns with multiple values (like "IRB1 and IRB2")
  - `category`: For columns with repeated values (saves memory)
  - `int32`, `float32`: For numeric data

- **default_type**: All columns not specified above will be treated as this type (usually "string")

The converted parquet file will be saved to `public/lv_export.parquet` for web access.

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
├── data/               # Place CSV files here (contents ignored by git)
├  └── config/model.json
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

   - After running your python script, ensure your parquet file was placed in `public/lv_export.parquet`
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

### Installation Issues

5. **Python not installed or not recognized**

   - Windows: "python is not recognized as an internal or external command"
   - Mac/Linux: "command not found: python"
   - **Solution**: See [Python installation guide](https://realpython.com/installing-python/) and [PATH troubleshooting](https://realpython.com/add-python-to-path/)

6. **npm/node not recognized in terminal**

   - Error: "npm is not recognized" or "command not found: npm"
   - **Solution**: See [Node.js PATH setup](https://stackoverflow.com/questions/27864040/fixing-npm-path-in-windows-8-and-10) (Windows) or [macOS/Linux PATH guide](https://stackoverflow.com/questions/11177954/how-do-i-completely-uninstall-node-js-and-reinstall-from-beginning-mac-os-x)
   - After installing Node.js, restart your terminal/PowerShell completely

7. **Python package installation errors**

   - Error: "pip is not recognized" or permission denied
   - **Solution**: See [pip installation guide](https://pip.pypa.io/en/stable/installation/) and [permission issues](https://stackoverflow.com/questions/31512422/pip-install-access-denied-on-windows)
   - Try using `python -m pip install` instead of `pip install`

8. **PowerShell execution policy errors** (Windows)
   - Error: "cannot be loaded because running scripts is disabled"
   - **Solution**: See [PowerShell execution policy guide](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies)
   - Or use Command Prompt (cmd) instead of PowerShell

### Getting More Help

- **Python issues**: Check [Python.org documentation](https://docs.python.org/3/using/index.html)
- **Node.js issues**: Check [Node.js troubleshooting guide](https://nodejs.org/en/docs/guides/debugging-getting-started/)
- **Still stuck?**: Include the full error message and your OS version when asking for help
