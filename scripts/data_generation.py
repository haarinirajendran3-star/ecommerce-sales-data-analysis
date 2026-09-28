import numpy as np
import pandas as pd
from pathlib import Path

np.random.seed(42)

BASE = Path(__file__).resolve().parents[1]
DATA_DIR = BASE / "data"
DATA_DIR.mkdir(exist_ok=True)

N = 7500

cities = {
    "Chennai": "Tamil Nadu",
    "Bengaluru": "Karnataka",
    "Hyderabad": "Telangana",
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Delhi": "Delhi",
    "Kolkata": "West Bengal",
    "Coimbatore": "Tamil Nadu",
    "Madurai": "Tamil Nadu",
    "Kochi": "Kerala",
}

products = [
    ("P001", "Wireless Earbuds", "Electronics", 2499, 1550),
    ("P002", "Smart Watch", "Electronics", 3999, 2500),
    ("P003", "Bluetooth Speaker", "Electronics", 2999, 1850),
    ("P004", "Laptop Backpack", "Accessories", 1499, 800),
    ("P005", "Phone Case", "Accessories", 699, 300),
    ("P006", "USB-C Cable", "Accessories", 499, 190),
    ("P007", "Running Shoes", "Fashion", 3299, 1900),
    ("P008", "Casual Shirt", "Fashion", 1799, 950),
    ("P009", "Denim Jeans", "Fashion", 2499, 1350),
    ("P010", "Coffee Maker", "Home & Kitchen", 5499, 3500),
    ("P011", "Air Fryer", "Home & Kitchen", 6999, 4400),
    ("P012", "Water Bottle", "Home & Kitchen", 899, 420),
    ("P013", "Notebook Set", "Stationery", 399, 160),
    ("P014", "Desk Organizer", "Stationery", 799, 330),
    ("P015", "Pen Set", "Stationery", 299, 100),
]
product_df = pd.DataFrame(products, columns=["Product_ID","Product_Name","Category","Unit_Price","Cost"])

customer_ids = [f"C{i:04d}" for i in range(1, 1601)]
names = ["Aarav", "Ananya", "Arjun", "Diya", "Ishaan", "Kavya", "Rahul", "Priya",
         "Rohan", "Meera", "Vikram", "Nisha", "Aditya", "Sneha", "Karthik", "Divya"]

customer_city = np.random.choice(list(cities.keys()), size=len(customer_ids))
customer_gender = np.random.choice(["Male", "Female"], size=len(customer_ids), p=[0.52, 0.48])
customer_age = np.random.randint(18, 61, size=len(customer_ids))
customer_name = [f"{np.random.choice(names)} {chr(65 + np.random.randint(26))}." for _ in customer_ids]

customers = pd.DataFrame({
    "Customer_ID": customer_ids,
    "Customer_Name": customer_name,
    "Gender": customer_gender,
    "Age": customer_age,
    "City": customer_city
})
customers["State"] = customers["City"].map(cities)

# Dates across one year
dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
order_dates = np.random.choice(dates, size=N)

# Slightly seasonal demand
month = pd.Series(order_dates).dt.month.to_numpy()
weights = np.ones(N)
weights += np.where(np.isin(month, [10,11,12]), 0.30, 0)
weights += np.where(np.isin(month, [3,4]), 0.08, 0)
weights = weights / weights.sum()

# Re-sample customers/products with business-like popularity
customer_idx = np.random.choice(len(customers), size=N, p=np.ones(len(customers))/len(customers))
product_probs = np.array([0.11,0.10,0.08,0.08,0.07,0.06,0.08,0.07,0.06,0.05,0.04,0.07,0.05,0.04,0.04])
product_probs = product_probs/product_probs.sum()
product_idx = np.random.choice(len(product_df), size=N, p=product_probs)

rows = []
for i in range(N):
    c = customers.iloc[customer_idx[i]]
    p = product_df.iloc[product_idx[i]]
    qty = np.random.choice([1,2,3,4], p=[0.58,0.28,0.10,0.04])
    discount = np.random.choice([0, .05, .10, .15, .20, .25], p=[.20,.20,.28,.18,.10,.04])
    # A small set of suspicious discounts for cleaning demonstration
    if np.random.rand() < 0.006:
        discount = np.random.choice([.50, .75, 1.20])
    sales = qty * p["Unit_Price"] * (1 - discount)
    cost = qty * p["Cost"]
    profit = sales - cost
    status = np.random.choice(["Delivered","Delivered","Delivered","Shipped","Cancelled","Returned"],
                              p=[.55,.15,.08,.08,.09,.05])
    rows.append([
        f"ORD{i+1:05d}", order_dates[i], c["Customer_ID"], c["Customer_Name"],
        c["Gender"], c["Age"], c["City"], c["State"], p["Product_ID"],
        p["Product_Name"], p["Category"], qty, p["Unit_Price"], discount,
        sales, cost, profit, np.random.choice(["UPI","Credit Card","Debit Card","Net Banking","Cash on Delivery"],
                                               p=[.36,.24,.17,.13,.10]), status
    ])

cols = ["Order_ID","Order_Date","Customer_ID","Customer_Name","Gender","Age","City","State",
        "Product_ID","Product_Name","Category","Quantity","Unit_Price","Discount","Sales",
        "Cost","Profit","Payment_Method","Order_Status"]
df = pd.DataFrame(rows, columns=cols)

# Add realistic data-quality issues
rng = np.random.default_rng(42)

# Missing values
for col, frac in [("Age",0.012), ("Payment_Method",0.008), ("City",0.006), ("Discount",0.006)]:
    idx = rng.choice(df.index, size=max(1,int(len(df)*frac)), replace=False)
    df.loc[idx, col] = np.nan

# Inconsistent categories/cities
city_idx = rng.choice(df.index, size=35, replace=False)
df.loc[city_idx[:12], "City"] = "chennai"
df.loc[city_idx[12:22], "City"] = "CHENNAI "
df.loc[city_idx[22:30], "City"] = "Bengaluru "
df.loc[city_idx[30:], "City"] = "mumbai"

cat_idx = rng.choice(df.index, size=25, replace=False)
df.loc[cat_idx[:10], "Category"] = "electronics "
df.loc[cat_idx[10:18], "Category"] = "FASHION"
df.loc[cat_idx[18:], "Category"] = "home & kitchen"

# Invalid values
bad_discount_idx = rng.choice(df.index, size=12, replace=False)
df.loc[bad_discount_idx, "Discount"] = [1.10, -0.05, 1.50, -0.10, 2.00, 1.25, -0.20, 1.40, -0.15, 1.80, -0.30, 1.10]

bad_age_idx = rng.choice(df.index, size=8, replace=False)
df.loc[bad_age_idx, "Age"] = [5, 9, 105, 120, -2, 130, 7, 150]

# Duplicate records
dupes = df.sample(35, random_state=42)
df = pd.concat([df, dupes], ignore_index=True)

# Recalculate financial columns for the raw file where possible, preserving intentional bad discount values
df.to_csv(DATA_DIR / "raw_sales_data.csv", index=False)

print(f"Created {len(df):,} raw rows at {DATA_DIR / 'raw_sales_data.csv'}")
print("The raw dataset intentionally contains missing, duplicate, inconsistent and invalid values.")
