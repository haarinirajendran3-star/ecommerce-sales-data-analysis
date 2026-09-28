# E-Commerce Sales & Customer Analytics Dashboard

## 1. Project Overview

This project simulates the work of a Junior Data Analyst for an online retail company.

The company has one year of transaction data and wants to understand:
- Sales performance
- Customer behavior
- Product performance
- Profitability
- Monthly trends
- Payment behavior
- Order status

The project follows:

**Data Cleaning → EDA → KPI Analysis → Visualization → Business Insights → Dashboard**

## 2. Business Problem

Management needs a simple analytical view of sales and customer performance to support decisions about products, pricing, discounts, customer retention and sales performance.

## 3. Objective

- Clean a realistic raw dataset
- Identify data-quality problems
- Perform exploratory data analysis
- Calculate business KPIs
- Answer business questions
- Create useful visualizations
- Produce an Excel executive dashboard
- Generate data-supported business insights

## 4. Dataset

The project generates approximately 7,500 raw transaction rows.

Columns include:
- Order_ID
- Order_Date
- Customer_ID
- Customer_Name
- Gender
- Age
- City
- State
- Product_ID
- Product_Name
- Category
- Quantity
- Unit_Price
- Discount
- Sales
- Cost
- Profit
- Payment_Method
- Order_Status

The raw data intentionally includes missing values, duplicate rows, inconsistent text values and invalid values so the cleaning stage resembles a real analytics workflow.

## 5. Tools

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Excel

## 6. Data Cleaning

The cleaning pipeline:
1. Loads the raw CSV
2. Inspects shape, types, missing values and duplicates
3. Converts dates
4. Standardizes text fields
5. Removes duplicate rows
6. Converts numeric fields
7. Handles invalid ages
8. Handles missing categorical values
9. Validates discount values
10. Recalculates Sales, Cost and Profit
11. Creates Month, Year and Profit_Margin fields

## 7. EDA

The project examines:
- Monthly revenue and profit
- Category sales and profit
- Product performance
- City performance
- Payment methods
- Customer age
- Gender-wise sales
- Discount versus profit
- Order status

## 8. KPIs

- Total Revenue
- Total Profit
- Total Orders
- Total Quantity Sold
- Total Customers
- Average Order Value
- Average Profit per Order
- Profit Margin
- Repeat Customers
- Top-Selling Product
- Top Product Category
- Best Performing City
- Best Performing Month

## 9. Visualizations

Generated charts:
- Monthly Revenue Trend
- Monthly Profit Trend
- Sales by Category
- Profit by Category
- Top 10 Products
- Top Cities
- Payment Methods
- Discount vs Profit
- Customer Age Distribution
- Sales by Gender
- Order Status Distribution

## 10. Dashboard

The Excel dashboard contains KPI cards and charts for:
- Revenue
- Profit
- Orders
- Customers
- Average Order Value
- Profit Margin
- Repeat Customers
- Cancelled Order Percentage
- Monthly sales
- Category performance
- Product performance

## 11. Key Findings

The Python analysis prints the findings calculated from the generated dataset. No business insight should be claimed until the analysis has been run.

## 12. Business Recommendations

Recommendations should be based on the calculated results. Examples of areas to consider:
- Focus on high-revenue/high-margin categories
- Review products with high sales but weak margins
- Investigate high discount levels
- Improve cancellation/return rates
- Develop retention strategies for repeat customers
- Monitor underperforming cities or months

## 13. How to Run

### Step 1: Open the project

Open `ecommerce-data-analysis` in VS Code.

### Step 2: Install packages

```bash
pip install -r requirements.txt
```

### Step 3: Generate raw data

```bash
python scripts/data_generation.py
```

### Step 4: Clean, analyze and create outputs

```bash
python scripts/data_cleaning.py
```

### Step 5: Open the results

Check:
- `data/raw_sales_data.csv`
- `data/cleaned_sales_data.csv`
- `visualizations/`
- `dashboard/ecommerce_dashboard.xlsx`

## 14. Future Improvements

- Add Power BI dashboard
- Add automated data refresh
- Add customer segmentation
- Add cohort analysis
- Add SQL database integration
- Add automated reporting
