import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load and clean data
def load_data():
    dfdem = pd.read_csv('Demographics - Lebanon 2023.csv')
    dfedu = pd.read_csv('Education - Lebanon 2023.csv')
    
    # Standardize column names
    dfedu.columns = dfedu.columns.str.strip().str.replace("illeterate", "illiterate")
    
    # Identify relevant education columns
    edu_cols = [col for col in dfedu.columns if 'percentageofeducationlevel' in col.lower()]
    
    merged = dfdem.merge(dfedu[["Town"] + edu_cols], on="Town", how="inner")
    return merged.drop_duplicates(subset="Town").reset_index(drop=True)

data = load_data()

# Initial headers
st.header('Lebanon Education and Family Size Analysis')
st.subheader('A dashboard showcasing family sizes and education profiles in Lebanese towns.')

# Add introductory text
st.markdown("Below is a brief analysis of family sizes and education profiles in Lebanese towns. Use the slider below to filter towns by minimum illiteracy rate.")

# Slider (Filter)
with st.sidebar:
    st.header("🔍 Filter")
    min_illiteracy = st.slider(
        "Minimum Illiteracy Rate (%)",
        min_value=0, max_value=10, value=0, step=1,
        help="Filter towns by minimum illiteracy percentage"
    )

# Filter data
illiteracy_col = next(col for col in data.columns if 'illiterate' in col.lower() and 'percentage' in col.lower())
filtered_data = data[data[illiteracy_col] >= min_illiteracy]

# Education mapping
edu_mapping = {
    'illiterate': 'Illiterate',
    'elementary': 'Elementary',
    'intermediate': 'Intermediate',
    'secondary': 'Secondary',
    'vocational': 'Vocational',
    'highereducation': 'Higher Education',
    'university': 'University'
}
edu_cols_found = {}
for key, label in edu_mapping.items():
    for col in filtered_data.columns:
        if key.lower() in col.lower() and 'percentage' in col.lower():
            edu_cols_found[col] = label
            break

# Main Information Dashboard
st.subheader("📋 Main Information")
st.markdown("This section provides a brief summary of the filtered data.")

fs_cols = [
    "Average family size - 1 to 3 members",
    "Average family size - 4 to 6 members",
    "Average family size - 7 or more members "
]

if not filtered_data.empty:
    # Calculate summary statistics
    total_towns = filtered_data["Town"].nunique()
    avg_illiteracy = filtered_data[illiteracy_col].mean()
    avg_family_size = filtered_data[fs_cols].mean().mean()

    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Towns", total_towns)
    col2.metric("Avg Illiteracy Rate (%)", f"{avg_illiteracy:.2f}")
    col3.metric("Avg Family Size", f"{avg_family_size:.2f}")
else:
    st.warning("No towns match the selected criteria. Summary statistics cannot be displayed.")

# Family Size Chart
st.subheader("📊 Family Size Distribution")
st.markdown("This chart displays the distribution of average family sizes across Lebanese towns.")

fs_data = filtered_data[fs_cols].sum()

fig_bar = go.Figure(go.Bar(
    x=["1-3", "4-6", "7+"],
    y=fs_data,
    marker=dict(color=['#86c5da', '#add8e6', '#d4ebf2'])
))
fig_bar.update_layout(
    height=400,
    margin=dict(l=40, r=20, t=40, b=40),
    plot_bgcolor='white',
    xaxis=dict(title="Average Family Size", linecolor='gray', showgrid=False),
    yaxis=dict(title="Towns", showgrid=False)
)
st.plotly_chart(fig_bar, use_container_width=True)

# Education Profile Chart
st.subheader("📈 Education Profile")
st.markdown("This radar chart illustrates the average educational profiles of Lebanese towns.")

if not filtered_data.empty and edu_cols_found:
    edu_means = filtered_data[list(edu_cols_found.keys())].mean()
    edu_means.index = edu_means.index.map(edu_cols_found)
    max_val = max(edu_means.max(), 10)
else:
    edu_means = pd.Series(0, index=list(edu_mapping.values()))
    max_val = 10

fig_polar = go.Figure(go.Scatterpolar(
    r=edu_means.values,
    theta=edu_means.index,
    fill='toself',
    line=dict(color='#2B3467'),
    marker=dict(color='#2B3467'),
    fillcolor='rgba(186, 215, 233, 0.5)'
))
fig_polar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, range=[0, max_val], showgrid=False),
        angularaxis=dict(showline=True, linecolor='gray', showgrid=False)
    ),
    height=500,
    margin=dict(l=40, r=40, t=60, b=40)
)

if filtered_data.empty:
    st.warning("No towns match the selected criteria")
elif not edu_cols_found:
    st.error("Missing education columns in the data")
else:
    st.plotly_chart(fig_polar, use_container_width=True)

# Footer
st.markdown('<p class="footer">Developed by Mazen Abou Chaar</p>', unsafe_allow_html=True)
st.markdown('<p class="footer">📊 Data Source: Lebanon 2023 Demographic Survey</p>', unsafe_allow_html=True)
