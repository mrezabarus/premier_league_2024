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
team_salary = pd.read_csv("team_salary.csv")
standing = pd.read_csv("standings.csv")


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
    title='Top 10 Teams by Total Goals'
)



col1, spacer, col2 = st.columns([3.5, 0.5, 6])
with col1:
    # Tampilkan
    st.altair_chart(chart, use_container_width=True)



##################### distribusi gaji pemain #####################
salaries['Team'] = salaries['Team'].str.strip()
highest_paid = salaries.loc[salaries.groupby('Team')['Weekly'].idxmax()][['Team','Player','Weekly']]
highest_paid = highest_paid.rename(columns={
    'Player': 'Highest Paid Player',
    'Weekly': 'Highest Wage'
})

lowest_paid = salaries.loc[salaries.groupby('Team')['Weekly'].idxmin()][['Team','Player','Weekly']]
lowest_paid = lowest_paid.rename(columns={
    'Player': 'Lowest Paid Player',
    'Weekly': 'Lowest Wage'
})

avg_wage = salaries.groupby('Team')['Weekly'].mean().reset_index()
avg_wage = avg_wage.rename(columns={'Weekly':'Average Wage'})

wage_summary = highest_paid.merge(lowest_paid, on='Team')
wage_summary = wage_summary.merge(avg_wage, on='Team')



with col2:
    st.subheader("Summary of Player Salaries by Club")
    st.dataframe(
        wage_summary.sort_values(by="Average Wage", ascending=False).reset_index(drop=True),
        use_container_width=True,
        hide_index=True    
    )


#menggabungkan 2 dataframe
df_perf = pd.merge(players, salaries, left_on="name", right_on="Player", how="inner")
df_perf.rename(columns={'name':'player_name'}, inplace=True)
st.subheader("Performance vs Salaries")
chart_perf = alt.Chart(df_perf).mark_circle(size=60).encode(
    x=alt.X("Weekly", title="salaries"),
    y=alt.Y("goals", title="Total Goals"),
    color='position',
    tooltip=['player_name','Weekly','goals','position']
).interactive().properties(
    height=400
)
st.altair_chart(chart_perf, use_container_width=True)


tab1, tab2, tab3, tab4= st.tabs([ "Filter Club", "Wage Distribution" ,"Salaries vs Rank", "compare two clubs salaries"])



with tab1:
    stats_with_salaries = pd.merge(players, salaries, left_on="name", right_on="Player", how="inner").reset_index()
    result_stats_with_salaries = stats_with_salaries[['Player','nation','Position','Team','age','played','starts','minutes','Weekly']]
    
    club_options = sorted(result_stats_with_salaries['Team'].unique())
    default_index = club_options.index("Liverpool") if "Liverpool" in club_options else 0
    selected_club = st.selectbox("Choose Club", club_options, index=default_index)

    #filter
    filtered = result_stats_with_salaries[result_stats_with_salaries['Team'] == selected_club]
    st.subheader(f"Played in {selected_club}")
    df_show = (
        filtered[['Player','Position','age','played','starts','minutes','Weekly']]
        .sort_values(by='Weekly', ascending=False)
        .reset_index(drop=True)
    )
    df_show.index = df_show.index + 1
    df_show.index.name = 'No'
    st.dataframe(df_show)

with tab2:

    # Tampilkan
    #st.altair_chart(chart, use_container_width=True)
    st.subheader("Distribution wage per Position")
    fig, ax = plt.subplots(figsize=(10,3))
    sns.boxplot(data=salaries.merge(players, left_on="Player", right_on="name", how="inner"), x='Position', y='Weekly', ax=ax)
    plt.xticks(rotation=45)
    st.pyplot(fig)

with tab3:
    standing_vs_salary = pd.merge(standing, team_salary, left_on="team", right_on="team", how="inner").reset_index(drop=True).sort_values(by="weekly", ascending=False)
    result = standing_vs_salary[['rank','team','win','loss','draw','goals','conceded','top_scorer','keeper','players','weekly','annual']]
    st.dataframe(result)
    
with tab4:

    stats_with_salaries_a = pd.merge(players, salaries, left_on="name", right_on="Player", how="inner").reset_index()
    result_stats_with_salaries_a = stats_with_salaries_a[['Player','nation','Position','Team','age','played','starts','minutes','Weekly']]

    col1, col2 = st.columns(2)
    
    with col1:    
        club_options_a = sorted(result_stats_with_salaries_a['Team'].unique())
        default_index_a = club_options_a.index("Liverpool") if "Liverpool" in club_options_a else 0
        st.container()
        selected_club_a = st.selectbox("Choose First Club", club_options_a, index=default_index_a)

        #filter
        filtered = result_stats_with_salaries_a[result_stats_with_salaries_a['Team'] == selected_club_a]
        st.subheader(f"Played in {selected_club}")
        df_show = (
            filtered[['Player','Position','age','played','starts','minutes','Weekly']]
            .sort_values(by='Weekly', ascending=False)
            .reset_index(drop=True)
        )
        df_show.index = df_show.index + 1
        df_show.index.name = 'No'
        st.dataframe(df_show)
    
    with col2:    
        club_options_b = sorted(result_stats_with_salaries_a['Team'].unique())
        default_index_b = club_options_b.index("Liverpool") if "Liverpool" in club_options_b else 0
        st.container()
        selected_club_b = st.selectbox("Choose Second Club", club_options_b, index=default_index_b)

        #filter
        filtered = result_stats_with_salaries_a[result_stats_with_salaries_a['Team'] == selected_club_b]
        st.subheader(f"Played in {selected_club_b}")
        df_show = (
            filtered[['Player','Position','age','played','starts','minutes','Weekly']]
            .sort_values(by='Weekly', ascending=False)
            .reset_index(drop=True)
        )
        df_show.index = df_show.index + 1
        df_show.index.name = 'No'
        st.dataframe(df_show)
