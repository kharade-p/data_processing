import requests
import pandas as pd
import io
import sqlite3
import json

def read_data_from_csv(url,region):
    df = pd.read_csv(url,delimiter=",", quotechar='"')
    df['Region'] = region  # Add region identifier
    return df

def transform_data(df):
    print("Before Shape: ", df.shape)
    df.drop_duplicates(subset=['OrderId'], keep='first', inplace=True)
    print("After Shape: ", df.shape)
    df['TotalSales'] = df['QuantityOrdered'] * df['ItemPrice']
    # Convert Price column from string to dictionary
    df['PromotionDiscount'] = df['PromotionDiscount'].apply(json.loads)  # Converts JSON string to dict

    # Normalize the JSON column while keeping other columns
    df_normalized = pd.json_normalize(df['PromotionDiscount'])

    # Merge normalized columns back with the original DataFrame
    df = pd.concat([df.drop(columns=['PromotionDiscount']), df_normalized], axis=1)

    # Convert Amount to float
    df['Amount'] = df['Amount'].astype(float)
    # print(df['Amount'])
    df['NetSale'] = df['TotalSales'] - df['Amount']
    df = df[df['NetSale'] > 0]  # Exclude negative or zero sales
    df = df.rename(columns={"Amount":"DiscountAmount",
                            "batch_id":"BatchId"})
    return df

def load_to_database(df, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    df.to_sql('sales_data', conn, if_exists='replace', index=False)
    conn.close()

def insert_data_to_db(df, db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS sales_data (
        OrderId TEXT PRIMARY KEY,
        OrderItemId TEXT,
        QuantityOrdered INTEGER,
        ItemPrice REAL,
        BatchId REAL,
        Region TEXT,
        TotalSales REAL,
        CurrencyCode TEXT,
        DiscountAmount REAL,
        NetSale REAL 
    );
    """
    cursor.execute(create_table_query)

    # Insert transformed data
    insert_query = """
    INSERT OR IGNORE INTO sales_data 
    (OrderId, OrderItemId, QuantityOrdered, ItemPrice, BatchId, Region, 
    TotalSales,CurrencyCode ,
    DiscountAmount, NetSale) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?,?,?);
    """
    
    data_tuples = df.to_records(index=False).tolist()
    cursor.executemany(insert_query, data_tuples)

    conn.commit()
    conn.close()

def validate_data(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    queries = {
        "Total Records": "SELECT COUNT(*) FROM sales_data;",
        "Sales by Region": "SELECT Region, SUM(TotalSales) FROM sales_data GROUP BY Region;",
        "Average Sales per Transaction": "SELECT AVG(TotalSales) FROM sales_data;",
        "Check Duplicate OrderId": "SELECT OrderId, COUNT(*) FROM sales_data GROUP BY OrderId HAVING COUNT(*) > 1;"
    }
    for desc, query in queries.items():
        print(f"{desc}:", cursor.execute(query).fetchall())
    conn.close()


if __name__ == "__main__":
    region_a_df = read_data_from_csv(r'/Users/tusharphalke/Downloads/order_region_a(in).csv',
                                     "A")
    region_b_df =read_data_from_csv(r'/Users/tusharphalke/Downloads/order_region_b(in).csv',
                                    "B")
    combined_data = pd.concat([region_a_df,region_b_df])
    df = transform_data(combined_data)
    print(df.columns)
    # load_to_database(df, "sales.db")
    insert_data_to_db(df,"sales.db")
    validate_data("sales.db")



# -- Total number of records
# SELECT COUNT(*) FROM sales_data;

# -- Total sales by region
# SELECT Region, SUM(TotalSales) FROM sales_data GROUP BY Region;

# -- Average sales amount per transaction
# SELECT AVG(NetSale) FROM sales_data;

# -- Ensure no duplicate OrderIds
# SELECT OrderId, COUNT(*) FROM sales_data GROUP BY OrderId HAVING COUNT(*) > 1;