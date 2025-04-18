import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import joblib
from model import predict_category
import os

# OpenAI API Key (Replace with your actual API Key)
#key = "enter your api_key!"
#openai.api_key = key

st.set_page_config(page_title="AI Expense Tracker", layout="wide")
st.title("💰 💵 Expense Tracker")

# User Login
user = st.sidebar.text_input("Enter Username")
if user:
    st.sidebar.success(f"Welcome, {user}!")

# Currency Selection
currency = st.sidebar.selectbox("Select Currency", ["USD", "INR", "EUR", "JPY"])
currency_symbols = {"USD": "$", "INR": "₹", "EUR": "€", "JPY": "¥"}

# Expense Categories
categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Travel", "Others"]
category = st.sidebar.selectbox("Select Category", categories)

# If Others is selected
if category == "Others":
    custom_category = st.sidebar.text_input("Enter Category Type")
    if custom_category:
        category = custom_category

# Expense Input Form
st.sidebar.header("Log New Expense")
description = st.sidebar.text_input("Expense Description")
amount = st.sidebar.number_input(f"Amount ({currency_symbols[currency]})", min_value=0, step=10)
date = st.sidebar.date_input("Date")

# Receipt Upload
directory = "receipts"
os.makedirs(directory, exist_ok=True)
uploaded_file = st.sidebar.file_uploader("Upload Receipt (Optional)", type=["jpg", "png"])

receipt_path = ""
if uploaded_file:
    receipt_path = os.path.join(directory, uploaded_file.name)
    with open(receipt_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

# Load or Create Expense Data
file_path = "expenses.csv"
if os.path.exists(file_path):
    expenses = pd.read_csv(file_path)
else:
    expenses = pd.DataFrame(columns=["User", "Date", "Description", "Amount", "Currency", "Category", "Receipt"])

# Add New Expense
if st.sidebar.button("Add Expense"):
    if user and description and amount and date:
        new_expense = {"User": user, "Date": date, "Description": description, "Amount": amount,
                       "Currency": currency, "Category": category, "Receipt": receipt_path}
        expenses = pd.concat([expenses, pd.DataFrame([new_expense])], ignore_index=True)
        expenses.to_csv(file_path, index=False)
        st.sidebar.success(f"Expense categorized as **{category}** and added!")
    else:
        st.sidebar.error("Please fill all fields!")

# Clear Expense Data
if st.sidebar.button("Clear All Expenses"):
    if os.path.exists(file_path):
        os.remove(file_path)
        expenses = pd.DataFrame(columns=["User", "Date", "Description", "Amount", "Currency", "Category", "Receipt"])
        st.sidebar.success("All expenses deleted permanently!")

# Display Expenses
if not expenses.empty:
    expenses["Date"] = pd.to_datetime(expenses["Date"])
    expenses["Month"] = expenses["Date"].dt.strftime("%Y-%m")
    
    if user:
        expenses = expenses[expenses["User"] == user]
    
    st.dataframe(expenses)
    
    # View Receipt Feature
    selected_receipt = st.selectbox("View Receipt for Expense", expenses["Receipt"].dropna().unique(), index=None)
    if selected_receipt:
        st.image(selected_receipt, caption="Uploaded Receipt", use_column_width=True)
    
    # Monthly Expense Selection
    months = expenses["Month"].unique()
    selected_month = st.selectbox("Select Month to View Breakdown", months)
    monthly_data = expenses[expenses["Month"] == selected_month]
    
    # Visualization - Monthly Expense 
    st.subheader(f"📊 Expense Breakdown for {selected_month}")
    colors = sns.color_palette("husl", len(categories))
    fig, ax = plt.subplots()
    sns.barplot(x=monthly_data["Category"].value_counts().index, y=monthly_data["Category"].value_counts().values, ax=ax, palette=colors)
    ax.set_ylabel(f"Total Expense ({currency_symbols[currency]})")
    ax.set_xlabel("Category")
    st.pyplot(fig)
    
    # Pie Chart for Category-Wise Spending
    st.subheader("📊 Category-Wise Spending")
    selected_pie_month = st.selectbox("Select Month for Pie Chart", months)
    pie_data = expenses[expenses["Month"] == selected_pie_month]
    fig_pie = px.pie(pie_data, names="Category", values="Amount", title=f"Category-wise Spending for {selected_pie_month}")
    st.plotly_chart(fig_pie)
    
    # Monthly Trend Line Graph
    st.subheader("📈 Monthly Expense Trend")
    monthly_expenses = expenses.groupby(["Month", "Category"]).sum(numeric_only=True).reset_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=monthly_expenses, x="Month", y="Amount", hue="Category", marker='o', ax=ax)
    ax.set_ylabel(f"Total Expense ({currency_symbols[currency]})")
    ax.set_xlabel("Month")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    st.pyplot(fig)
    
    # Chatbot Integration
    
