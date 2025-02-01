import streamlit as st


def apply_date_filter(df):
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=df['date'].min().date(),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date()
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=df['date'].max().date(),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date()
        )

    if start_date > end_date:
        st.error("End date must be after start date")
        st.stop()

    mask = (df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)
    filtered_df = df[mask]

    if len(filtered_df) == 0:
        st.error("No data available for the selected date range. Please select different dates.")
        st.stop()

    return filtered_df


def apply_sentiment_filter(df):
    sentiment_options = ['Positive', 'Neutral', 'Negative']
    selected_sentiments = st.multiselect(
        "Select Sentiment",
        options=sentiment_options,
        default=sentiment_options
    )
    if selected_sentiments:
        sentiment_mask = df['sentiment'].isin(selected_sentiments)
        df = df[sentiment_mask]
    return df


def apply_word_filters(df):
    include_words_input = st.text_input(
        "Include Posts with Words (comma-separated)",
        help="Enter words separated by commas to only include posts containing these words."
    )
    if include_words_input:
        include_words = [word.strip().lower() for word in include_words_input.split(',') if word.strip()]
        if include_words:
            include_mask = df['content'].str.lower().str.contains('|'.join(include_words), regex=True)
            df = df[include_mask]

    exclude_words_input = st.text_input(
        "Exclude Posts with Words (comma-separated)",
        help="Enter words separated by commas to exclude posts containing these words."
    )
    if exclude_words_input:
        exclude_words = [word.strip().lower() for word in exclude_words_input.split(',') if word.strip()]
        if exclude_words:
            exclude_mask = ~df['content'].str.lower().str.contains('|'.join(exclude_words), regex=True)
            df = df[exclude_mask]

    return df


def apply_numeric_filter(df, column, label):
    min_val = int(df[column].min())
    max_val = int(df[column].max())

    if min_val == max_val:
        st.markdown(f"*All {'posts' if column == 'likes' else 'users'} have **{min_val}** {column}*")
        return df

    value_range = st.slider(
        f"Number of {label}",
        min_value=min_val,
        max_value=max_val,
        value=(min_val, max_val)
    )
    mask = (df[column] >= value_range[0]) & (df[column] <= value_range[1])
    return df[mask]


def apply_user_filter(df):
    # Get users sorted by total views
    user_views = df.groupby('user_name')['views'].sum().sort_values(ascending=False)
    user_options = ['All Users'] + list(user_views.index)

    selected_user = st.selectbox(
        "Filter by User (Ranked by Views)",
        options=user_options,
        format_func=lambda x: f"{x} ({int(user_views[x]):,} views)" if x != 'All Users' else x
    )

    if selected_user != 'All Users':
        df = df[df['user_name'] == selected_user]

    return df


def display_filters(df):
    with st.sidebar:
        st.markdown("""
            <div style='padding: 1rem 0; border-bottom: 1px solid #e2e8f0;'>
                <h3 style='font-size: 1.25rem; font-weight: 600; color: #1e293b;'>
                    Dashboard Filters
                </h3>
                <p style='color: #64748b; font-size: 0.875rem;'>
                    Refine your data view
                </p>
            </div>
        """, unsafe_allow_html=True)
        try:
            filtered_df = apply_date_filter(df)
            filtered_df = apply_user_filter(filtered_df)
            filtered_df = apply_sentiment_filter(filtered_df)
            filtered_df = apply_word_filters(filtered_df)
            filtered_df = apply_numeric_filter(filtered_df, 'likes', 'Likes')
            filtered_df = apply_numeric_filter(filtered_df, 'followers', 'Followers')

            if len(filtered_df) == 0:
                st.error("No data available after applying the selected filters. Please adjust your filter criteria.")
                st.stop()

            return filtered_df

        except Exception as e:
            st.error(f"Error with filter selection: {str(e)}")
            st.stop()