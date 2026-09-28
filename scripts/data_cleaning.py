import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
VIZ_DIR = BASE / "visualizations"
DASH_DIR = BASE / "dashboard"
VIZ_DIR.mkdir(exist_ok=True)
DASH_DIR.mkdir(exist_ok=True)

sns.set_theme(style="whitegrid")

raw_path = DATA_DIR / "raw_sales_data.csv"
clean_path = DATA_DIR / "cleaned_sales_data.csv"

df = pd.read_csv(raw_path)

print("\n========== 1. RAW DATA INSPECTION ==========")
print("Shape:", df.shape)
print("\nData types:")
print(df.dtypes)
print("\nMissing values:")
print(df.isna().sum())
print("\nDuplicate rows:", df.duplicated().sum())

# Date conversion
df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

# Standardize text fields
text_cols = ["Customer_Name","Gender","City","State","Product_Name","Category","Payment_Method","Order_Status"]
for col in text_cols:
    df[col] = df[col].astype("string").str.strip()

df["City"] = df["City"].replace({
    "chennai":"Chennai", "CHENNAI":"Chennai", "Bengaluru":"Bengaluru",
    "mumbai":"Mumbai", "Mumbai":"Mumbai"
})
df["Category"] = df["Category"].str.title()
df["Category"] = df["Category"].replace({
    "Home & Kitchen":"Home & Kitchen",
    "Electronics":"Electronics",
    "Fashion":"Fashion",
    "Accessories":"Accessories",
    "Stationery":"Stationery"
})

# Remove exact duplicate rows
df = df.drop_duplicates().copy()

# Numeric conversion
numeric_cols = ["Age","Quantity","Unit_Price","Discount","Sales","Cost","Profit"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Handle invalid age
df.loc[(df["Age"] < 18) | (df["Age"] > 80), "Age"] = np.nan
df["Age"] = df["Age"].fillna(df["Age"].median()).round().astype(int)

# Handle missing categorical values
df["Payment_Method"] = df["Payment_Method"].fillna(df["Payment_Method"].mode()[0])
df["City"] = df["City"].fillna("Unknown")

# Fix invalid discounts
df.loc[(df["Discount"] < 0) | (df["Discount"] > 0.50), "Discount"] = np.nan
df["Discount"] = df["Discount"].fillna(df["Discount"].median())

# Recalculate financial values after cleaning
df["Sales"] = df["Quantity"] * df["Unit_Price"] * (1 - df["Discount"])
df["Cost"] = df["Quantity"] * (df["Cost"] / df["Quantity"].replace(0, np.nan))
# The expression above preserves per-unit cost from the raw data.
df["Cost"] = df["Cost"].fillna(0)
df["Profit"] = df["Sales"] - df["Cost"]

# Useful calculated columns
df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)
df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Year"] = df["Order_Date"].dt.year
df["Profit_Margin"] = np.where(df["Sales"] != 0, df["Profit"] / df["Sales"], 0)

# Mark cancelled/returned orders separately for operational analysis.
# Revenue KPIs below use delivered + shipped orders, excluding cancelled/returned.
valid_sales = df[df["Order_Status"].isin(["Delivered","Shipped"])].copy()

df.to_csv(clean_path, index=False)

print("\n========== 2. CLEANING SUMMARY ==========")
print("Cleaned shape:", df.shape)
print("Duplicates after cleaning:", df.duplicated().sum())
print("Missing values after cleaning:")
print(df.isna().sum())

# ----------------------------
# KPI calculations
# ----------------------------
total_revenue = valid_sales["Sales"].sum()
total_profit = valid_sales["Profit"].sum()
total_orders = len(valid_sales)
total_quantity = valid_sales["Quantity"].sum()
total_customers = valid_sales["Customer_ID"].nunique()
average_order_value = total_revenue / total_orders if total_orders else 0
average_profit_order = total_profit / total_orders if total_orders else 0
profit_margin = total_profit / total_revenue if total_revenue else 0

customer_orders = valid_sales.groupby("Customer_ID")["Order_ID"].nunique()
repeat_customers = int((customer_orders > 1).sum())

top_product_units = valid_sales.groupby("Product_Name")["Quantity"].sum().sort_values(ascending=False)
top_product_revenue = valid_sales.groupby("Product_Name")["Sales"].sum().sort_values(ascending=False)
category_sales = valid_sales.groupby("Category")["Sales"].sum().sort_values(ascending=False)
category_profit = valid_sales.groupby("Category")["Profit"].sum().sort_values(ascending=False)
city_sales = valid_sales.groupby("City")["Sales"].sum().sort_values(ascending=False)
monthly_sales = valid_sales.groupby("Month")["Sales"].sum()
monthly_profit = valid_sales.groupby("Month")["Profit"].sum()

cancelled_pct = (df["Order_Status"].eq("Cancelled").mean() * 100)

print("\n========== 3. BUSINESS KPIs ==========")
print(f"Total Revenue: ₹{total_revenue:,.2f}")
print(f"Total Profit: ₹{total_profit:,.2f}")
print(f"Total Orders (Delivered/Shipped): {total_orders:,}")
print(f"Total Quantity Sold: {total_quantity:,}")
print(f"Total Customers: {total_customers:,}")
print(f"Average Order Value: ₹{average_order_value:,.2f}")
print(f"Average Profit per Order: ₹{average_profit_order:,.2f}")
print(f"Profit Margin: {profit_margin:.2%}")
print(f"Repeat Customers: {repeat_customers:,}")
print(f"Top-Selling Product by Units: {top_product_units.index[0]}")
print(f"Top Product by Revenue: {top_product_revenue.index[0]}")
print(f"Top Category by Sales: {category_sales.index[0]}")
print(f"Top Category by Profit: {category_profit.index[0]}")
print(f"Best Performing City: {city_sales.index[0]}")
print(f"Best Performing Month: {monthly_sales.idxmax()}")
print(f"Cancelled Orders: {cancelled_pct:.2f}%")

# ----------------------------
# Business question tables
# ----------------------------
top10_customers = (valid_sales.groupby(["Customer_ID","Customer_Name"])["Sales"]
                   .sum().sort_values(ascending=False).head(10).reset_index())

product_summary = (valid_sales.groupby(["Product_ID","Product_Name"])
                   .agg(Sales=("Sales","sum"), Profit=("Profit","sum"), Quantity=("Quantity","sum"))
                   .reset_index())
product_summary["Profit_Margin"] = product_summary["Profit"] / product_summary["Sales"]
high_sales_low_profit = product_summary.sort_values(["Sales","Profit_Margin"], ascending=[False, True]).head(5)

low_sales_high_margin = product_summary.sort_values(["Profit_Margin","Sales"], ascending=[False, True]).head(5)

# Discount relationship
discount_corr = valid_sales[["Discount","Profit"]].corr().iloc[0,1]

# ----------------------------
# Visualizations
# ----------------------------
plt.figure(figsize=(10,5))
monthly_sales.plot(marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(VIZ_DIR / "monthly_sales.png", dpi=150)
plt.close()

plt.figure(figsize=(10,5))
monthly_profit.plot(marker="o")
plt.title("Monthly Profit Trend")
plt.xlabel("Month")
plt.ylabel("Profit (₹)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(VIZ_DIR / "monthly_profit.png", dpi=150)
plt.close()

plt.figure(figsize=(9,5))
category_sales.sort_values().plot(kind="barh")
plt.title("Sales by Category")
plt.xlabel("Sales (₹)")
plt.tight_layout()
plt.savefig(VIZ_DIR / "category_sales.png", dpi=150)
plt.close()

plt.figure(figsize=(9,5))
category_profit.sort_values().plot(kind="barh")
plt.title("Profit by Category")
plt.xlabel("Profit (₹)")
plt.tight_layout()
plt.savefig(VIZ_DIR / "category_profit.png", dpi=150)
plt.close()

plt.figure(figsize=(10,6))
top_product_revenue.head(10).sort_values().plot(kind="barh")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(VIZ_DIR / "top_products.png", dpi=150)
plt.close()

plt.figure(figsize=(10,6))
city_sales.head(10).sort_values().plot(kind="barh")
plt.title("Top Cities by Revenue")
plt.xlabel("Revenue (₹)")
plt.tight_layout()
plt.savefig(VIZ_DIR / "city_sales.png", dpi=150)
plt.close()

payment_counts = valid_sales["Payment_Method"].value_counts()
plt.figure(figsize=(7,7))
plt.pie(payment_counts.values, labels=payment_counts.index, autopct="%1.1f%%", startangle=90)
plt.title("Payment Method Distribution")
plt.tight_layout()
plt.savefig(VIZ_DIR / "payment_methods.png", dpi=150)
plt.close()

plt.figure(figsize=(8,5))
sns.scatterplot(data=valid_sales.sample(min(2500, len(valid_sales)), random_state=42),
                x="Discount", y="Profit", alpha=0.5)
plt.title("Discount vs Profit")
plt.xlabel("Discount")
plt.ylabel("Profit (₹)")
plt.tight_layout()
plt.savefig(VIZ_DIR / "discount_vs_profit.png", dpi=150)
plt.close()

plt.figure(figsize=(8,5))
sns.histplot(valid_sales["Age"], bins=15, kde=True)
plt.title("Customer Age Distribution")
plt.xlabel("Age")
plt.tight_layout()
plt.savefig(VIZ_DIR / "customer_age.png", dpi=150)
plt.close()

gender_sales = valid_sales.groupby("Gender")["Sales"].sum()
plt.figure(figsize=(7,5))
gender_sales.plot(kind="bar")
plt.title("Sales by Gender")
plt.ylabel("Sales (₹)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(VIZ_DIR / "gender_sales.png", dpi=150)
plt.close()

status_counts = df["Order_Status"].value_counts()
plt.figure(figsize=(8,5))
status_counts.sort_values().plot(kind="barh")
plt.title("Order Status Distribution")
plt.xlabel("Number of Orders")
plt.tight_layout()
plt.savefig(VIZ_DIR / "order_status.png", dpi=150)
plt.close()

# ----------------------------
# Excel dashboard workbook
# ----------------------------
with pd.ExcelWriter(DASH_DIR / "ecommerce_dashboard.xlsx", engine="xlsxwriter") as writer:
    valid_sales.to_excel(writer, sheet_name="Clean Sales", index=False)
    pd.DataFrame({
        "KPI": ["Total Revenue","Total Profit","Total Orders","Total Customers",
                "Average Order Value","Profit Margin","Repeat Customers"],
        "Value": [total_revenue,total_profit,total_orders,total_customers,
                  average_order_value,profit_margin,repeat_customers]
    }).to_excel(writer, sheet_name="Dashboard_Data", index=False)
    monthly_sales.rename("Revenue").to_frame().to_excel(writer, sheet_name="Monthly Analysis")
    monthly_profit.rename("Profit").to_frame().to_excel(writer, sheet_name="Monthly Profit")
    category_sales.rename("Sales").to_frame().to_excel(writer, sheet_name="Category Sales")
    category_profit.rename("Profit").to_frame().to_excel(writer, sheet_name="Category Profit")
    top_product_revenue.head(10).rename("Revenue").to_frame().to_excel(writer, sheet_name="Top Products")
    city_sales.head(10).rename("Revenue").to_frame().to_excel(writer, sheet_name="Top Cities")
    payment_counts.rename("Orders").to_frame().to_excel(writer, sheet_name="Payment Methods")
    top10_customers.to_excel(writer, sheet_name="Top Customers", index=False)
    high_sales_low_profit.to_excel(writer, sheet_name="High Sales Low Profit", index=False)
    low_sales_high_margin.to_excel(writer, sheet_name="High Margin Products", index=False)

    workbook = writer.book
    dash = workbook.add_worksheet("Executive Dashboard")
    writer.sheets["Executive Dashboard"] = dash

    title_fmt = workbook.add_format({"bold":True,"font_size":20,"align":"center","valign":"vcenter"})
    kpi_label = workbook.add_format({"bold":True,"align":"center","border":1})
    kpi_value = workbook.add_format({"bold":True,"font_size":14,"align":"center","border":1,"num_format":"₹#,##0.00"})
    pct_fmt = workbook.add_format({"bold":True,"font_size":14,"align":"center","border":1,"num_format":"0.00%"})
    num_fmt = workbook.add_format({"bold":True,"font_size":14,"align":"center","border":1,"num_format":"#,##0"})

    dash.merge_range("A1:H2", "E-Commerce Sales & Customer Analytics Dashboard", title_fmt)

    cards = [
        ("A4","A5","Total Revenue", total_revenue, kpi_value),
        ("C4","C5","Total Profit", total_profit, kpi_value),
        ("E4","E5","Total Orders", total_orders, num_fmt),
        ("G4","G5","Total Customers", total_customers, num_fmt),
        ("A7","A8","Average Order Value", average_order_value, kpi_value),
        ("C7","C8","Profit Margin", profit_margin, pct_fmt),
        ("E7","E8","Repeat Customers", repeat_customers, num_fmt),
        ("G7","G8","Cancelled %", cancelled_pct/100, pct_fmt),
    ]
    for c1,c2,label,value,fmt in cards:
        dash.write(c1, label, kpi_label)
        dash.write(c2, value, fmt)

    dash.set_column("A:H", 18)
    dash.set_row(0, 28)

    # Add chart images created by the analysis
    images = [
        ("A10", VIZ_DIR / "monthly_sales.png"),
        ("E10", VIZ_DIR / "category_sales.png"),
        ("A27", VIZ_DIR / "category_profit.png"),
        ("E27", VIZ_DIR / "top_products.png"),
    ]
    for cell, path in images:
        dash.insert_image(cell, str(path), {"x_scale":0.55,"y_scale":0.55})

print("\n========== 4. BUSINESS INSIGHTS ==========")
print(f"1. {category_sales.index[0]} generated the highest revenue.")
print(f"2. {category_profit.index[0]} generated the highest profit.")
print(f"3. {city_sales.index[0]} was the highest-revenue city.")
print(f"4. {monthly_sales.idxmax()} was the strongest month by revenue.")
print(f"5. {monthly_sales.idxmin()} was the weakest month by revenue.")
print(f"6. {top_product_units.index[0]} sold the most units.")
print(f"7. {top_product_revenue.index[0]} generated the highest product revenue.")
print(f"8. The most-used payment method was {payment_counts.index[0]}.")
print(f"9. Cancelled orders represented {cancelled_pct:.2f}% of all raw orders.")
print(f"10. Discount vs profit correlation in valid sales was {discount_corr:.3f}.")

print("\nTop 10 customers by revenue:")
print(top10_customers.to_string(index=False))

print("\nHigh-sales / lower-margin candidates:")
print(high_sales_low_profit[["Product_Name","Sales","Profit","Profit_Margin"]].to_string(index=False))

print("\nHigh-margin candidates:")
print(low_sales_high_margin[["Product_Name","Sales","Profit","Profit_Margin"]].to_string(index=False))

print("\nProject outputs created successfully.")
