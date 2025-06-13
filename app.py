import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import joblib
import os
from model import predict_category  # Make sure this file exists

# App Config
st.set_page_config(page_title="Expense Tracker", layout="wide")
st.title("💰Expense Tracker")

# Sidebar: User Login
user = st.sidebar.text_input("Enter Username")
if user:
    st.sidebar.success(f"Welcome, {user}!")

# Sidebar: Currency Selection
currency = st.sidebar.selectbox("Select Currency", ["USD", "INR", "EUR", "JPY"])
currency_symbols = {"USD": "$", "INR": "₹", "EUR": "€", "JPY": "¥"}

# Sidebar: Category Selection
categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Travel", "Others"]
category = st.sidebar.selectbox("Select Category", categories)
if category == "Others":
    custom_category = st.sidebar.text_input("Enter Custom Category")
    if custom_category:
        category = custom_category

# Sidebar: New Expense Form
st.sidebar.header("Log New Expense")
description = st.sidebar.text_input("Expense Description")
amount = st.sidebar.number_input(f"Amount ({currency_symbols[currency]})", min_value=0.0, step=10.0)
date = st.sidebar.date_input("Date")

# Predict category if possible
if description and not category and user:
    try:
        predicted = predict_category(description)
        st.sidebar.info(f"Predicted Category: {predicted}")
    except:
        pass  # If model import fails, do nothing

# Sidebar: File Upload
receipt_path = ""
directory = os.path.join("receipts", user if user else "default")
os.makedirs(directory, exist_ok=True)
uploaded_file = st.sidebar.file_uploader("Upload Receipt (Optional)", type=["jpg", "png"])
if uploaded_file:
    receipt_path = os.path.join(directory, uploaded_file.name)
    with open(receipt_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

# Load/Create Data
file_path = "expenses.csv"
if os.path.exists(file_path):
    expenses = pd.read_csv(file_path)
else:
    expenses = pd.DataFrame(columns=["User", "Date", "Description", "Amount", "Currency", "Category", "Receipt"])

# Add Expense
if st.sidebar.button("Add Expense"):
    if user and description and amount and date:
        new_expense = {
            "User": user,
            "Date": date,
            "Description": description,
            "Amount": amount,
            "Currency": currency,
            "Category": category,
            "Receipt": receipt_path if uploaded_file else None
        }
        expenses = pd.concat([expenses, pd.DataFrame([new_expense])], ignore_index=True)
        expenses.to_csv(file_path, index=False)
        st.sidebar.success(f"Expense categorized as **{category}** and added!")
    else:
        st.sidebar.error("Please fill all fields!")

# Clear All Expenses
if st.sidebar.button("Clear All Expenses"):
    if os.path.exists(file_path):
        os.remove(file_path)
        expenses = pd.DataFrame(columns=["User", "Date", "Description", "Amount", "Currency", "Category", "Receipt"])
        st.sidebar.success("All expenses deleted permanently!")

# Display & Visualize
if not expenses.empty:
    expenses["Date"] = pd.to_datetime(expenses["Date"])
    expenses["Month"] = expenses["Date"].dt.strftime("%Y-%m")
    expenses["Date"] = expenses["Date"].dt.date

    # Filter user-specific
    if user:
        expenses = expenses[expenses["User"] == user].copy()

    st.subheader("📄 Expense Records")
    st.dataframe(expenses)

    # Download CSV
    csv = expenses.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="expenses.csv", mime="text/csv")

    # View Uploaded Receipt
    receipts = expenses["Receipt"].dropna().unique()
    if receipts.size > 0:
        selected_receipt = st.selectbox("📷 View Uploaded Receipt", receipts)
        if selected_receipt:
            st.image(selected_receipt, caption="Receipt", use_column_width=True)

    # Monthly Breakdown
    months = expenses["Month"].unique()
    if months.size > 0:
        selected_month = st.selectbox("📆 Select Month", months)
        monthly_data = expenses[expenses["Month"] == selected_month]

        st.markdown(f"### 💸 Total Spent in {selected_month}: {currency_symbols[currency]}{monthly_data['Amount'].sum():,.2f}")

        st.subheader("📊 Category Breakdown - Bar Chart")
        colors = sns.color_palette("husl", len(categories))
        fig, ax = plt.subplots()
        sns.barplot(
            x=monthly_data["Category"].value_counts().index,
            y=monthly_data["Category"].value_counts().values,
            ax=ax, palette=colors
        )
        ax.set_ylabel("Number of Transactions")
        ax.set_xlabel("Category")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30)
        st.pyplot(fig)

        st.subheader("🧁 Category-Wise Spending - Pie Chart")
        fig_pie = px.pie(monthly_data, names="Category", values="Amount", title=f"Spending for {selected_month}")
        st.plotly_chart(fig_pie)

        st.subheader("📈 Monthly Expense Trend")
        monthly_expenses = expenses.groupby(["Month", "Category"]).sum(numeric_only=True).reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=monthly_expenses, x="Month", y="Amount", hue="Category", marker='o', ax=ax)
        ax.set_ylabel(f"Total Expense ({currency_symbols[currency]})")
        ax.set_xlabel("Month")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
