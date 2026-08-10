
import streamlit as st
import pandas as pd
import os
from datetime import datetime
import joblib


st.set_page_config(
    page_title="Banking Credit & Cross-Sell Engine",
    page_icon="🏦",
    layout="wide"
)


MODEL_FILE = "credit_risk_model.pkl"
DATA_FILE = "credit_risk_default.csv"


@st.cache_resource
def load_model():
    return joblib.load(MODEL_FILE)


model = load_model()


def recommend_loan(intent):

    recommendations = {
        "PERSONAL": "Personal Loan",
        "EDUCATION": "Education Loan",
        "MEDICAL": "Medical Loan",
        "HOMEIMPROVEMENT": "Home Improvement Loan",
        "DEBTCONSOLIDATION": "Debt Consolidation Loan",
        "VENTURE": "Business / Venture Loan"
    }

    return recommendations.get(
        intent,
        "Personal Loan"
    )


def recommend_products(
    intent,
    income,
    home_ownership
):

    products = []

    if income >= 50000:
        products.append("Credit Card")

    products.append("Savings Account")

    if home_ownership == "RENT":
        products.append("Home Loan")

    if intent == "MEDICAL":
        products.append("Health Insurance")

    if intent == "EDUCATION":
        products.append("Education Savings Plan")

    if intent == "VENTURE":
        products.append("Business Banking Account")

    if intent == "HOMEIMPROVEMENT":
        products.append("Home Insurance")

    return list(dict.fromkeys(products))


def get_customer_data():

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100,
        value=25
    )

    income = st.number_input(
        "Annual Income",
        min_value=0,
        value=30000,
        step=1000
    )

    home_ownership = st.selectbox(
        "Home Ownership",
        ["RENT", "OWN", "MORTGAGE", "OTHER"]
    )

    employment_length = st.number_input(
        "Employment Length (years)",
        min_value=0.0,
        max_value=50.0,
        value=3.0,
        step=1.0
    )

    credit_history = st.number_input(
        "Credit History Length (years)",
        min_value=0,
        max_value=50,
        value=5
    )

    previous_default = st.selectbox(
        "Previous Default on File",
        ["N", "Y"]
    )

    loan_intent = st.selectbox(
        "Loan Purpose",
        [
            "PERSONAL",
            "EDUCATION",
            "MEDICAL",
            "HOMEIMPROVEMENT",
            "DEBTCONSOLIDATION",
            "VENTURE"
        ]
    )

    loan_amount = st.number_input(
        "Loan Amount",
        min_value=500,
        value=10000,
        step=500
    )

    loan_grade = st.selectbox(
        "Loan Grade",
        ["A", "B", "C", "D", "E", "F", "G"]
    )

    interest_rate = st.number_input(
        "Interest Rate (%)",
        min_value=1.0,
        max_value=30.0,
        value=10.0,
        step=0.1
    )

    loan_percent_income = (
        loan_amount / income
        if income > 0
        else 0
    )

    return {
        "person_age": age,
        "person_income": income,
        "person_home_ownership": home_ownership,
        "person_emp_length": employment_length,
        "loan_intent": loan_intent,
        "loan_grade": loan_grade,
        "loan_amnt": loan_amount,
        "loan_int_rate": interest_rate,
        "loan_percent_income": loan_percent_income,
        "cb_person_default_on_file": previous_default,
        "cb_person_cred_hist_length": credit_history
    }


st.title("🏦 Banking Credit & Cross-Sell Engine")

st.write(
    "A machine learning system for loan assessment "
    "and banking product recommendations."
)


portal = st.sidebar.radio(
    "Select Portal",
    [
        "Customer Portal",
        "Staff Portal"
    ]
)


# ============================================================
# CUSTOMER PORTAL
# ============================================================

if portal == "Customer Portal":

    st.header("👤 Customer Portal")

    st.write(
        "Enter your information to find a suitable "
        "loan and banking products."
    )

    st.divider()

    customer_data = get_customer_data()

    st.divider()

    st.subheader("Recommended Loan")

    recommended_loan = recommend_loan(
        customer_data["loan_intent"]
    )

    st.success(
        f"Recommended Loan: **{recommended_loan}**"
    )

    products = recommend_products(
        customer_data["loan_intent"],
        customer_data["person_income"],
        customer_data["person_home_ownership"]
    )

    st.subheader("Recommended Banking Products")

    for product in products:
        st.write(f"✓ {product}")

    st.divider()

    if st.button(
        "Submit Application",
        type="primary",
        use_container_width=True
    ):

        if os.path.exists(DATA_FILE):

            existing_data = pd.read_csv(DATA_FILE)

            if (
                not existing_data.empty
                and "customer_id" in existing_data.columns
            ):
                customer_id = (
                    pd.to_numeric(
                        existing_data["customer_id"],
                        errors="coerce"
                    ).max() + 1
                )
            else:
                customer_id = 1

        else:

            customer_id = 1

        record = customer_data.copy()

        record["customer_id"] = int(customer_id)

        record["recommended_loan"] = recommended_loan

        record["recommended_products"] = (
            ", ".join(products)
        )

        record["staff_decision"] = "Pending"

        record["accepted_product"] = ""

        record["submission_date"] = (
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        new_customer = pd.DataFrame([record])

        if os.path.exists(DATA_FILE):

            new_customer.to_csv(
                DATA_FILE,
                mode="a",
                header=False,
                index=False
            )

        else:

            new_customer.to_csv(
                DATA_FILE,
                index=False
            )

        st.success(
            "Application submitted successfully!"
        )

        st.info(
            f"Your Application ID is: {int(customer_id)}"
        )


# ============================================================
# STAFF PORTAL
# ============================================================

else:

    st.header("👨‍💼 Staff Portal")

    st.write(
        "Internal banking dashboard for customer "
        "risk assessment and cross-selling."
    )

    st.divider()

    if not os.path.exists(DATA_FILE):

        st.warning(
            "No customer applications found yet."
        )

        st.stop()

    customers = pd.read_csv(DATA_FILE)

    if customers.empty:

        st.warning(
            "No customer applications found."
        )

        st.stop()

    # Make decision columns safe for text values.
    if "staff_decision" not in customers.columns:
        customers["staff_decision"] = "Pending"

    if "accepted_product" not in customers.columns:
        customers["accepted_product"] = ""

    customers["staff_decision"] = (
        customers["staff_decision"]
        .astype("object")
    )

    customers["accepted_product"] = (
        customers["accepted_product"]
        .astype("object")
    )

    customer_ids = customers[
        "customer_id"
    ].tolist()

    selected_id = st.selectbox(
        "Select Customer",
        customer_ids
    )

    customer = customers[
        customers["customer_id"] == selected_id
    ].iloc[0]

    st.divider()

    st.subheader("Customer Information")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Age",
        int(customer["person_age"])
    )

    col2.metric(
        "Income",
        f"₹{float(customer['person_income']):,.0f}"
    )

    col3.metric(
        "Loan Amount",
        f"₹{float(customer['loan_amnt']):,.0f}"
    )

    col4.metric(
        "Loan Purpose",
        customer["loan_intent"]
    )

    st.divider()

    st.subheader("Loan Information")

    loan_data = pd.DataFrame({
        "Field": [
            "Loan Intent",
            "Loan Grade",
            "Loan Amount",
            "Interest Rate",
            "Loan / Income",
            "Home Ownership",
            "Previous Default"
        ],

        "Value": [
            customer["loan_intent"],
            customer["loan_grade"],
            f"₹{float(customer['loan_amnt']):,.0f}",
            f"{float(customer['loan_int_rate']):.2f}%",
            f"{float(customer['loan_percent_income']):.2%}",
            customer["person_home_ownership"],
            customer["cb_person_default_on_file"]
        ]
    })

    st.table(loan_data)

    st.divider()

    # ========================================================
    # CREDIT RISK
    # ========================================================

    st.subheader("🔐 Credit Risk Assessment")

    age = float(customer["person_age"])
    income = float(customer["person_income"])
    loan_amount = float(customer["loan_amnt"])

    loan_to_income = (
        loan_amount / max(income, 1)
    )

    income_to_loan = (
        income / max(loan_amount, 1)
    )

    if age <= 25:
        age_group = "Young"
    elif age <= 35:
        age_group = "Adult"
    elif age <= 50:
        age_group = "Middle_Age"
    else:
        age_group = "Senior"

    if income <= 25000:
        income_group = "Low"
    elif income <= 50000:
        income_group = "Medium"
    elif income <= 100000:
        income_group = "High"
    else:
        income_group = "Very_High"

    model_features = pd.DataFrame([{

        "person_age":
            customer["person_age"],

        "person_income":
            customer["person_income"],

        "person_home_ownership":
            customer["person_home_ownership"],

        "person_emp_length":
            customer["person_emp_length"],

        "loan_intent":
            customer["loan_intent"],

        "loan_grade":
            customer["loan_grade"],

        "loan_amnt":
            customer["loan_amnt"],

        "loan_int_rate":
            customer["loan_int_rate"],

        "loan_percent_income":
            customer["loan_percent_income"],

        "cb_person_default_on_file":
            customer["cb_person_default_on_file"],

        "cb_person_cred_hist_length":
            customer["cb_person_cred_hist_length"],

        "income_to_loan":
            income_to_loan,

        "loan_to_income":
            loan_to_income,

        "age_group":
            age_group,

        "income_group":
            income_group
    }])

    try:

        probability = model.predict_proba(
            model_features
        )[0][1]

        prediction = model.predict(
            model_features
        )[0]

        risk_percentage = probability * 100

        if risk_percentage < 30:
            risk = "Low Risk"

        elif risk_percentage < 60:
            risk = "Medium Risk"

        else:
            risk = "High Risk"

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Default Probability",
            f"{risk_percentage:.2f}%"
        )

        col2.metric(
            "Prediction",
            "Default"
            if prediction == 1
            else "No Default"
        )

        col3.metric(
            "Risk Level",
            risk
        )

    except Exception as error:

        st.error(
            "The model could not process this customer's "
            "information."
        )

        st.code(str(error))

        st.stop()

    st.divider()

    # ========================================================
    # CROSS-SELL
    # ========================================================

    st.subheader("💳 Cross-Sell Recommendation")

    staff_products = recommend_products(
        customer["loan_intent"],
        float(customer["person_income"]),
        customer["person_home_ownership"]
    )

    for product in staff_products:
        st.write(
            f"✓ **{product}**"
        )

    st.divider()

    # ========================================================
    # STAFF DECISION
    # ========================================================

    st.subheader("Staff Decision")

    selected_product = st.selectbox(
        "Select Product",
        staff_products
    )

    decision = st.radio(
        "Decision",
        [
            "Accept Recommendation",
            "Reject Recommendation"
        ]
    )

    if st.button(
        "Save Staff Decision",
        type="primary",
        use_container_width=True
    ):

        # Force these columns to accept text.
        customers["staff_decision"] = (
            customers["staff_decision"]
            .astype("object")
        )

        customers["accepted_product"] = (
            customers["accepted_product"]
            .astype("object")
        )

        mask = (
            customers["customer_id"]
            == selected_id
        )

        customers.loc[
            mask,
            "staff_decision"
        ] = decision

        if decision == "Accept Recommendation":

            customers.loc[
                mask,
                "accepted_product"
            ] = selected_product

        else:

            customers.loc[
                mask,
                "accepted_product"
            ] = ""

        customers.to_csv(
            DATA_FILE,
            index=False
        )

        st.success(
            "Staff decision saved successfully."
        )

        st.info(
            f"Customer {selected_id}: "
            f"{decision}"
        )

