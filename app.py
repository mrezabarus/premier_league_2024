import streamlit as st
import altair as alt
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Premier League 2025 Dashboard",
    layout="wide"
)

st.title("Premier League 2025 Dashboard")

fixtures = pd.read_csv("fixtures.csv")
players = pd.read_csv("player_stats.csv")
salaries = pd.read_csv("player_salaries.csv")


### TOP 10 Team Goals
fixtures['Home'] = fixtures['Home'].str.strip().str.title()
fixtures['Away'] = fixtures['Away'].str.strip().str.title()

home_goals = fixtures.groupby('Home')['HomeScore'].sum()
away_goals = fixtures.groupby('Away')['AwayScore'].sum()

#gabungan home dan away
total_goals = home_goals.add(away_goals, fill_value=0)

total_goals = pd.Series(total_goals)

#top 10 goals
top_10_goals = total_goals.sort_values(ascending=False).head(10)

df_goals = top_10_goals.reset_index()
df_goals.columns = ['Team','Total Goals']

# chart Altair
chart = alt.Chart(df_goals).mark_bar(color='steelblue').encode(
    x=alt.X('Team:N', sort='-y'),
    y=alt.Y('Total Goals:Q'),
    tooltip=['Team', 'Total Goals']
).properties(
    width=600,
    height=400,
    title='Top 10 Tim by Total Goals'
)



col1, spacer, col2 = st.columns([3.5, 0.5, 6])
with col1:
    # Tampilkan
    st.altair_chart(chart, use_container_width=True)



##################### distribusi gaji pemain #####################
salaries['Team'] = salaries['Team'].str.strip()
highest_paid = salaries.loc[salaries.groupby('Team')['Weekly'].idxmax()][['Team','Player','Weekly']]
highest_paid = highest_paid.rename(columns={
    'Player': 'Pemain Gaji Tertinggi',
    'Weekly': 'Gaji Tertinggi'
})

lowest_paid = salaries.loc[salaries.groupby('Team')['Weekly'].idxmin()][['Team','Player','Weekly']]
lowest_paid = lowest_paid.rename(columns={
    'Player': 'Pemain Gaji Terendah',
    'Weekly': 'Gaji Terendah'
})

avg_wage = salaries.groupby('Team')['Weekly'].mean().reset_index()
avg_wage = avg_wage.rename(columns={'Weekly':'Gaji Rata rata'})

wage_summary = highest_paid.merge(lowest_paid, on='Team')
wage_summary = wage_summary.merge(avg_wage, on='Team')



with col2:
    st.subheader("Gaji Pemain di Klub")
    st.dataframe(
        wage_summary.sort_values(by="Gaji Rata rata", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True    
    )


#menggabungkan 2 dataframe
df_perf = pd.merge(players, salaries, left_on="name", right_on="Player", how="inner")
df_perf.rename(columns={'name':'player_name'}, inplace=True)
st.subheader("Salaries VS Performance")
chart_perf = alt.Chart(df_perf).mark_circle(size=60).encode(
    x=alt.X("Weekly", title="salaries"),
    y=alt.Y("goals", title="Total Goals"),
    color='position',
    tooltip=['player_name','Weekly','goals','position']
).interactive().properties(
    height=400
)
st.altair_chart(chart_perf, use_container_width=True)


tab1, tab2= st.tabs([ "Filter Klub", "Distribusi Gaji"])



with tab1:
    club_options = sorted(salaries['Team'].unique())
    selected_club = st.selectbox("Pilih Klub", club_options)

    #filter
    filtered = salaries[salaries['Team'] == selected_club]
    st.subheader(f"Pemain di {selected_club}")
    df_show = (
        filtered[['Player','Position','Weekly']]
        .sort_values(by='Weekly', ascending=False)
        .reset_index(drop=True)
    )
    df_show.index = df_show.index + 1
    df_show.index.name = 'No'
    st.dataframe(df_show)

with tab2:

    # Tampilkan
    #st.altair_chart(chart, use_container_width=True)
    st.subheader("Distribusi gaji per posisi")
    fig, ax = plt.subplots(figsize=(10,3))
    sns.boxplot(data=salaries.merge(players, left_on="Player", right_on="name", how="inner"), x='position', y='Weekly', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)
    