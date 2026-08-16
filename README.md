# Personal Expense Tracker

A simple Flask web app to track daily income and expenses, built with
SQLite3, Pandas, and Matplotlib.

## Features
- Add, edit, and delete income/expense transactions
- Categorize transactions (Food, Transport, Housing, etc.)
- View running totals: income, expense, and balance
- Summary page with a pie chart of expenses by category
- Data stored locally in a SQLite database (`expenses.db`)

## Setup

1. **Install dependencies** (Python 3.9+ recommended):
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app**:
   ```bash
   python app.py
   ```

3. Open your browser to **http://127.0.0.1:5000**

The database file (`expenses.db`) and chart image (`static/chart.png`)
are created automatically the first time you run the app.

## Project Structure
```
expense_tracker/
├── app.py                 # Flask app: routes, DB logic, chart generation
├── requirements.txt
├── expenses.db             # created automatically on first run
├── templates/
│   ├── base.html           # shared layout & navigation
│   ├── index.html          # transaction list + totals
│   ├── add_edit.html       # add/edit transaction form
│   └── summary.html        # summary + pie chart
└── static/
    ├── style.css
    └── chart.png            # generated when you visit /summary
```

## Next Steps / Ideas to Extend
- Filter transactions by date range or category
- Export transactions to CSV using Pandas
- Add monthly bar chart alongside the category pie chart
- Add simple user login if multiple people will use it
