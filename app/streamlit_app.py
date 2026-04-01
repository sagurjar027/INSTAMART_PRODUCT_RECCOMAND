from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.predict import get_dashboard_overview, get_user_profile, recommend


st.set_page_config(page_title="Instacart Insight Hub", page_icon=":shopping_cart:", layout="wide")


PALETTE = {
    "emerald": "#0f766e",
    "teal": "#14b8a6",
    "amber": "#d97706",
    "ink": "#0f172a",
    "slate": "#475569",
    "mist": "#f8fafc",
    "coral": "#e11d48",
    "surface_light": "rgba(255, 255, 255, 0.72)",
    "surface_dark": "rgba(15, 23, 42, 0.62)",
    "border_light": "rgba(15, 23, 42, 0.10)",
    "border_dark": "rgba(248, 250, 252, 0.14)",
    "mint": "#99f6e4",
    "sand": "#fcd34d",
    "sky": "#7dd3fc",
    "grid_light": "rgba(15, 23, 42, 0.10)",
    "grid_dark": "rgba(248, 250, 252, 0.12)",
}

theme_base = (st.get_option("theme.base") or "light").lower()
is_dark_theme = theme_base == "dark"
metric_surface = PALETTE["surface_dark"] if is_dark_theme else PALETTE["surface_light"]
metric_border = PALETTE["border_dark"] if is_dark_theme else PALETTE["border_light"]
chart_font_color = PALETTE["mist"] if is_dark_theme else PALETTE["ink"]
chart_grid_color = PALETTE["grid_dark"] if is_dark_theme else PALETTE["grid_light"]
chart_template = "plotly_dark" if is_dark_theme else "plotly_white"


st.markdown(
    f"""
    <style>
        .stApp {{
            background:
                radial-gradient(circle at top left, rgba(20, 184, 166, 0.14), transparent 28%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.14), transparent 24%),
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--background-color, #ffffff) 96%, {PALETTE["teal"]} 4%) 0%,
                    color-mix(in srgb, var(--background-color, #ffffff) 92%, {PALETTE["amber"]} 8%) 100%
                );
            color: var(--text-color, #111827);
        }}
        .hero {{
            padding: 1.6rem 1.8rem;
            border-radius: 24px;
            color: #f8fafc;
            background:
                linear-gradient(135deg, rgba(15, 23, 42, 0.96) 0%, rgba(15, 118, 110, 0.94) 55%, rgba(20, 184, 166, 0.90) 100%);
            border: 1px solid rgba(255, 255, 255, 0.10);
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
            margin-bottom: 1rem;
        }}
        .hero h1 {{
            margin: 0;
            font-size: 2.3rem;
        }}
        .hero p {{
            margin: 0.5rem 0 0;
            font-size: 1rem;
            opacity: 0.9;
        }}
        .metric-card {{
            background: {metric_surface};
            border: 1px solid {metric_border};
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
            backdrop-filter: blur(14px);
        }}
        .metric-label {{
            color: color-mix(in srgb, var(--text-color, #111827) 72%, transparent);
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }}
        .metric-value {{
            color: var(--text-color, #111827);
            font-size: 1.7rem;
            font-weight: 700;
        }}
        .section-copy {{
            color: color-mix(in srgb, var(--text-color, #111827) 76%, transparent);
            margin-bottom: 1rem;
        }}
        [data-baseweb="tab-list"] {{
            gap: 0.35rem;
        }}
        [data-baseweb="tab"] {{
            background: color-mix(in srgb, var(--secondary-background-color, #f3f4f6) 88%, transparent);
            border-radius: 999px;
            padding-inline: 1rem;
        }}
        [data-baseweb="tab"][aria-selected="true"] {{
            background: color-mix(in srgb, var(--primary-color, {PALETTE["emerald"]}) 18%, var(--background-color, #ffffff));
            color: var(--text-color, #111827);
        }}
        [data-testid="stSidebar"] > div:first-child {{
            background:
                linear-gradient(
                    180deg,
                    color-mix(in srgb, var(--secondary-background-color, #f3f4f6) 94%, transparent),
                    color-mix(in srgb, var(--background-color, #ffffff) 98%, transparent)
                );
        }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_overview():
    return get_dashboard_overview()


@st.cache_data(show_spinner=False)
def load_local_recommendations(user_id: int, top_n: int) -> pd.DataFrame | None:
    return recommend(user_id=user_id, top_n=top_n)


@st.cache_resource(show_spinner=False)
def load_user_profile(user_id: int):
    return get_user_profile(user_id)


@st.cache_data(show_spinner=False)
def load_api_recommendations(user_id: int, top_n: int, api_url: str) -> pd.DataFrame:
    response = requests.get(
        f"{api_url.rstrip('/')}/recommend/{user_id}",
        params={"top_n": top_n},
        timeout=30,
    )
    response.raise_for_status()
    return pd.DataFrame(response.json())


def metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_chart_theme(fig, colorbar_title: str | None = None):
    fig.update_layout(
        template=chart_template,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=chart_font_color,
    )
    fig.update_xaxes(gridcolor=chart_grid_color, zerolinecolor=chart_grid_color)
    fig.update_yaxes(gridcolor=chart_grid_color, zerolinecolor=chart_grid_color)
    if colorbar_title is not None:
        fig.update_layout(coloraxis_colorbar_title=colorbar_title)
    return fig


def build_probability_chart(result: pd.DataFrame):
    chart_df = result.sort_values("prob", ascending=True)
    fig = px.bar(
        chart_df,
        x="prob",
        y="product_name",
        orientation="h",
        color="prob",
        color_continuous_scale=[PALETTE["mint"], PALETTE["emerald"], PALETTE["ink"]],
        title="Recommendation confidence by product",
        labels={"prob": "Probability", "product_name": "Product"},
        template=chart_template,
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_chart_theme(fig)


def build_user_vs_average_chart(profile: dict, summary: dict):
    compare_df = pd.DataFrame(
        {
            "Metric": ["Total orders", "Total products", "Reorder ratio"],
            "Selected user": [
                profile["total_orders"],
                profile["total_products"],
                profile["reorder_ratio"],
            ],
            "Platform average": [
                summary["avg_orders_per_user"],
                summary["avg_products_per_user"],
                summary["avg_reorder_ratio"],
            ],
        }
    ).melt(id_vars="Metric", var_name="Group", value_name="Value")

    fig = px.bar(
        compare_df,
        x="Metric",
        y="Value",
        color="Group",
        barmode="group",
        color_discrete_sequence=[PALETTE["emerald"], PALETTE["amber"]],
        title="Selected shopper vs platform benchmark",
        template=chart_template,
    )
    return apply_chart_theme(fig)


overview = load_overview()
summary = overview["summary"]
user_features = overview["user_features"]
product_features = overview["product_features"]
popular_products = overview["popular_products"]
reliable_products = overview["reliable_products"]


st.markdown(
    """
    <div class="hero">
        <h1>Instacart Insight Hub</h1>
        <p>Explore shopper behavior, product momentum, reorder trends, and personalized recommendations from one dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


with st.sidebar:
    st.header("Controls")
    use_api = st.toggle("Use FastAPI for recommendations", value=False)
    api_url = st.text_input("FastAPI base URL", value="http://127.0.0.1:8000")
    user_id = st.number_input("User ID", min_value=1, value=1, step=1)
    top_n = st.slider("Recommendations to show", min_value=5, max_value=20, value=10, step=1)
    fetch_button = st.button("Generate insights", type="primary", width="stretch")


metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("Users", f"{summary['total_users']:,}")
with metric_cols[1]:
    metric_card("Products", f"{summary['total_products']:,}")
with metric_cols[2]:
    metric_card("Avg Orders / User", f"{summary['avg_orders_per_user']:.1f}")
with metric_cols[3]:
    metric_card("Avg Reorder Ratio", f"{summary['avg_reorder_ratio']:.2%}")


st.markdown("### Platform insights")
st.markdown('<div class="section-copy">A quick read on customer loyalty, product traction, and high-repeat items across the catalog.</div>', unsafe_allow_html=True)

tab_overview, tab_products, tab_distribution = st.tabs(["Market pulse", "Product trends", "Behavior spread"])

with tab_overview:
    left, right = st.columns(2)
    with left:
        scatter_fig = px.scatter(
            user_features.sample(min(4000, len(user_features)), random_state=42),
            x="total_orders",
            y="total_products",
            color="reorder_ratio",
            color_continuous_scale=[PALETTE["sand"], PALETTE["amber"], PALETTE["emerald"]],
            title="Order volume vs product breadth",
            labels={
                "total_orders": "Total orders",
                "total_products": "Total products",
                "reorder_ratio": "Reorder ratio",
            },
            opacity=0.65,
            template=chart_template,
        )
        apply_chart_theme(scatter_fig, colorbar_title="Reorder")
        st.plotly_chart(scatter_fig, width="stretch")
    with right:
        reorder_hist = px.histogram(
            user_features,
            x="reorder_ratio",
            nbins=30,
            title="How reorder loyalty is distributed",
            color_discrete_sequence=[PALETTE["teal"]],
            labels={"reorder_ratio": "Reorder ratio"},
            template=chart_template,
        )
        apply_chart_theme(reorder_hist)
        st.plotly_chart(reorder_hist, width="stretch")

with tab_products:
    left, right = st.columns(2)
    with left:
        popular_fig = px.bar(
            popular_products.sort_values("product_orders"),
            x="product_orders",
            y="product_name",
            orientation="h",
            title="Most ordered products",
            color="product_orders",
            color_continuous_scale=[PALETTE["sky"], PALETTE["teal"], PALETTE["ink"]],
            template=chart_template,
        )
        popular_fig.update_layout(coloraxis_showscale=False)
        apply_chart_theme(popular_fig)
        st.plotly_chart(popular_fig, width="stretch")
    with right:
        reliable_fig = px.bar(
            reliable_products.sort_values("product_reorder_rate"),
            x="product_reorder_rate",
            y="product_name",
            orientation="h",
            title="Top reorder champions",
            color="product_reorder_rate",
            color_continuous_scale=[PALETTE["sand"], PALETTE["amber"], PALETTE["coral"]],
            labels={"product_reorder_rate": "Reorder rate"},
            template=chart_template,
        )
        reliable_fig.update_layout(coloraxis_showscale=False)
        apply_chart_theme(reliable_fig)
        st.plotly_chart(reliable_fig, width="stretch")

with tab_distribution:
    left, right = st.columns(2)
    with left:
        orders_hist = px.histogram(
            user_features,
            x="total_orders",
            nbins=35,
            title="Distribution of total orders",
            color_discrete_sequence=[PALETTE["emerald"]],
            template=chart_template,
        )
        apply_chart_theme(orders_hist)
        st.plotly_chart(orders_hist, width="stretch")
    with right:
        product_scatter = px.scatter(
            product_features.sample(min(4000, len(product_features)), random_state=7),
            x="product_orders",
            y="product_reorder_rate",
            title="Product demand vs reorderability",
            color="product_reorder_rate",
            color_continuous_scale=[PALETTE["sky"], PALETTE["teal"], PALETTE["ink"]],
            labels={"product_orders": "Product orders", "product_reorder_rate": "Reorder rate"},
            opacity=0.7,
            template=chart_template,
        )
        apply_chart_theme(product_scatter, colorbar_title="Reorder")
        st.plotly_chart(product_scatter, width="stretch")


st.markdown("### Personalized recommendations")
st.markdown('<div class="section-copy">Generate recommendations for a shopper and compare their behavior with platform-wide averages.</div>', unsafe_allow_html=True)


if fetch_button:
    profile = load_user_profile(user_id)
    if profile is None:
        st.error("User ID not found in the processed feature set.")
    else:
        try:
            with st.spinner("Building recommendation view..."):
                result = load_api_recommendations(user_id, top_n, api_url) if use_api else load_local_recommendations(user_id, top_n)
        except requests.HTTPError as exc:
            detail = "FastAPI request failed."
            try:
                payload = exc.response.json()
                detail = payload.get("detail", detail)
            except ValueError:
                pass
            st.error(detail)
            result = None
        except requests.RequestException:
            st.error("FastAPI is not reachable. Start the API server or switch off API mode.")
            result = None
        except Exception as exc:
            st.error(f"Unable to generate recommendations: {exc}")
            result = None

        if result is not None and not result.empty:
            user_metric_cols = st.columns(3)
            with user_metric_cols[0]:
                metric_card("Selected User Orders", f"{profile['total_orders']:,}")
            with user_metric_cols[1]:
                metric_card("Products Purchased", f"{profile['total_products']:,}")
            with user_metric_cols[2]:
                metric_card("User Reorder Ratio", f"{profile['reorder_ratio']:.2%}")

            rec_tab, compare_tab, table_tab = st.tabs(["Recommendations", "User benchmark", "Data table"])

            with rec_tab:
                left, right = st.columns([1.05, 1.25])
                with left:
                    st.plotly_chart(build_probability_chart(result), width="stretch")
                with right:
                    bubble_fig = px.scatter(
                        result,
                        x="product_orders",
                        y="product_reorder_rate",
                        size="prob",
                        color="prob",
                        hover_name="product_name",
                        color_continuous_scale=[PALETTE["mint"], PALETTE["emerald"], PALETTE["ink"]],
                        title="Recommended items by popularity and reorder rate",
                        labels={
                            "product_orders": "Historical product orders",
                            "product_reorder_rate": "Product reorder rate",
                            "prob": "Recommendation probability",
                        },
                        template=chart_template,
                    )
                    apply_chart_theme(bubble_fig, colorbar_title="Prob")
                    st.plotly_chart(bubble_fig, width="stretch")

            with compare_tab:
                st.plotly_chart(build_user_vs_average_chart(profile, summary), width="stretch")

            with table_tab:
                display_df = result.copy()
                display_df["prob"] = display_df["prob"].map(lambda value: f"{value:.2%}")
                display_df["product_reorder_rate"] = display_df["product_reorder_rate"].map(lambda value: f"{value:.2%}")
                st.dataframe(display_df, width="stretch", hide_index=True)
                st.download_button(
                    "Download recommendations as CSV",
                    data=result.to_csv(index=False).encode("utf-8"),
                    file_name=f"instacart_recommendations_user_{user_id}.csv",
                    mime="text/csv",
                )


st.markdown("---")
st.caption("Author: Sahil Kasana |       linkdin.com/in/sahil-kasana6055/")
st.caption("Data sourced from the Instacart Online Grocery Shopping Dataset 2017-2018, made available by Instacart on Kaggle. This dashboard is a demo built for educational purposes and is not affiliated with Instacart.")
st.caption("Built for faster merchandising insight, user discovery, and recommendation review.")
