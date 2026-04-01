# Instacart Recommendation System

This project builds a machine learning powered product recommendation system on top of the Instacart market basket dataset. It includes:

- data preparation and feature engineering in a Jupyter notebook
- an `XGBoost` recommendation model
- a `FastAPI` backend for serving predictions
- a `Streamlit` dashboard for recommendations, insights, and trend analysis

The current app can show platform-level shopping insights, product popularity trends, reorder behavior, and user-specific recommended products.

## Project Highlights

- Personalized recommendations for a selected `user_id`
- Interactive Streamlit dashboard with charts and KPI cards
- FastAPI endpoints for recommendation serving and summary insights
- Feature-engineered user and product tables stored as reusable CSVs
- Serialized model artifacts for easy loading in app and API layers

## Folder Structure

```text
INSTACART-Recommand/
|-- api/
|   `-- main.py                  # FastAPI app and endpoints
|-- app/
|   `-- streamlit_app.py         # Streamlit dashboard UI
|-- data/
|   `-- raw/
|       `-- processed/
|           |-- products.csv
|           |-- product_features.csv
|           |-- user_features.csv
|           `-- user_product.csv
|-- models/
|   |-- features.pkl             # Feature column list used for inference
|   `-- xgb_model.pkl            # Trained XGBoost model
|-- notebooks/
|   `-- instacart.ipynb          # End-to-end experimentation and training workflow
|-- src/
|   |-- data_loader.py           # Placeholder for future loading utilities
|   `-- predict.py               # Cached loaders, recommendations, dashboard helpers
|-- requirements.txt
`-- README.md
```

## Dataset Overview

This project follows the Instacart basket-analysis style workflow. The notebook uses the original Instacart CSVs such as:

- `orders.csv`
- `products.csv`
- `order_products__prior.csv`
- `order_products__train.csv`
- `aisles.csv`
- `departments.csv`

Those raw files are used in the notebook to build the processed assets currently stored in `data/raw/processed/`.

### Processed Data Used by the App

1. `user_features.csv`
   Derived customer-level behavioral features:
   - `user_id`
   - `total_orders`
   - `total_products`
   - `reorder_ratio`

2. `product_features.csv`
   Derived product-level behavioral features:
   - `product_id`
   - `product_orders`
   - `product_reorder_rate`

3. `user_product.csv`
   User-product interaction history:
   - `user_id`
   - `product_id`
   - `up_order_count`
   - `up_reorder_count`

4. `products.csv`
   Product metadata:
   - `product_id`
   - `product_name`
   - `aisle_id`
   - `department_id`

## End-to-End Approach

### 1. Data Loading

In the notebook, the raw Instacart CSV files are loaded into pandas DataFrames and joined together using order, user, and product keys.

### 2. Data Preparation

The `prior` order history is merged with:

- order information from `orders.csv`
- product information from `products.csv`

This creates a richer event table containing customer ordering behavior and product identity in one place.

### 3. Feature Engineering

The notebook builds three core feature tables.

#### User Features

Created by grouping on `user_id`:

- `total_orders`: maximum order number for the user
- `total_products`: total purchased items counted from prior history
- `reorder_ratio`: mean of reordered flag for that user

#### Product Features

Created by grouping on `product_id`:

- `product_orders`: number of times the product appears
- `product_reorder_rate`: mean reorder rate for the product

#### User-Product Features

Created by grouping on `user_id` and `product_id`:

- `up_order_count`: number of times a user bought a product
- `up_reorder_count`: number of times the product was reordered by that user

### 4. Training Dataset Creation

The training table is created by combining:

- train orders
- user-level features
- product-level features
- user-product interaction features

Missing values are filled and a final training file is produced in the notebook workflow.

### 5. Model Training

The notebook trains an `XGBClassifier` using these inference features:

- `total_orders`
- `total_products`
- `reorder_ratio`
- `product_orders`
- `product_reorder_rate`

Target:

- `reordered`

Train-test split is performed with:

- `test_size=0.2`
- `random_state=42`

### 6. Evaluation

The notebook reports the following metrics:

- F1 Score: `0.7659892000273417`
- Precision: `0.7251070346285332`
- Recall: `0.8117567518622705`

These numbers indicate the model captures reorder behavior reasonably well, with especially strong recall.

### 7. Model Export

The notebook saves:

- `models/xgb_model.pkl`
- `models/features.pkl`

These are used directly by the API and Streamlit application.

## Inference Flow

At inference time, `src/predict.py`:

1. loads the trained model and processed CSVs
2. filters `user_product.csv` for a specific `user_id`
3. merges the user and product feature tables
4. computes prediction probabilities with `predict_proba`
5. ranks products by recommendation score
6. returns the top products with metadata and behavioral columns

The prediction module now uses cached loaders so repeated requests are much faster after the first load.

## API Layer

`api/main.py` provides a FastAPI service with these endpoints:

- `GET /`
  Returns a welcome message

- `GET /health`
  Simple health check endpoint

- `GET /recommend/{user_id}?top_n=10`
  Returns top recommended products for a user

- `GET /insights/overview`
  Returns summary stats plus top popular and high-reorder products

## Streamlit Dashboard

`app/streamlit_app.py` provides a richer analytics and recommendation interface.

### Dashboard Features

- overview KPI cards
- reorder ratio distribution charts
- user behavior scatter plots
- most ordered products chart
- highest reorder-rate product chart
- personalized recommendation confidence chart
- user vs platform benchmark comparison
- downloadable recommendation CSV

### Current Insight Areas

- platform-wide shopping behavior
- product demand vs reorderability
- high-confidence personalized recommendations
- user-specific order and reorder profile

## How to Run

### 1. Create or Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run FastAPI

```powershell
python -m uvicorn api.main:app --reload
```

FastAPI docs will be available at:

- `http://127.0.0.1:8000/docs`

### 4. Run Streamlit

```powershell
streamlit run app/streamlit_app.py
```

The dashboard can run:

- in local model mode
- in FastAPI mode by toggling API usage in the sidebar

## Notebook Usage

The main experimentation and model-building workflow lives in:

- `notebooks/instacart.ipynb`

Use the notebook if you want to:

- regenerate processed feature CSVs
- retrain the recommendation model
- test alternative feature combinations
- inspect performance metrics
- experiment with additional EDA and feature engineering

## Approaches You Can Explore Next

This repository already uses a strong tabular ML approach, but there are several directions you can expand.

### Feature Engineering Improvements

- add recency features such as days since last order
- include aisle and department level aggregations
- add basket size and average reorder cycle features
- use user-product recency and frequency features

### Modeling Improvements

- tune XGBoost hyperparameters with cross-validation
- compare against LightGBM, CatBoost, or Random Forest
- train ranking-oriented models instead of only binary classification
- add calibration for better probability interpretation

### Recommendation Improvements

- filter out already saturated or low-interest items
- blend personalized score with product popularity
- add business rules for diversity across aisles and departments
- support top-N recommendations per department

### Product and UX Improvements

- persist precomputed recommendation candidates for faster cold starts
- add search and product drill-down in Streamlit
- expose model confidence and explanation hints
- add monitoring for API latency and usage

## Known Notes

- The first recommendation request can take longer because the large processed interaction file must be loaded into memory.
- Later requests are much faster because the prediction assets are cached.
- `src/data_loader.py` is currently a placeholder and can be used later for a cleaner data access layer.

## Tech Stack

- Python
- Pandas
- Scikit-learn
- XGBoost
- Joblib
- FastAPI
- Streamlit
- Plotly

## Author

Project author listed in the Streamlit app:

- Sahil Kasana
