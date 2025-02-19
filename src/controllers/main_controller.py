import traceback
import os
import streamlit as st
import pandas as pd

from src.models.data_model import (
    categorize_sentiment,
    get_hashtag_frequency,
    get_location_counts,
    get_sentiment,
    get_word_frequency,
    analyze_text_content,
    load_and_process_data,
)
from src.views.dashboard_view import (
    apply_custom_css,
    create_tabs,
    display_title,
)
from src.views.filters_view import display_filters
from src.views.metrics_view import (
    create_engagement_scatter,
    create_hashtag_chart,
    create_location_chart,
    create_pie_chart,
    create_time_series,
    create_user_table,
    create_word_freq_chart,
    display_metrics_with_icons,
)


def main():

    st.set_page_config(
        page_title="Targeted Therapies of Lung Cancer 2025",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    apply_custom_css()
    display_title()

    try:
        df = load_and_process_data()
        df['sentiment_score'] = df['content'].apply(get_sentiment)
        df['sentiment'] = df['sentiment_score'].apply(categorize_sentiment)

        filtered_df = display_filters(df)

        metrics = {
            'Total Posts': len(filtered_df),
            'Total Views': int(filtered_df['views'].sum()),
            'Total Reposts': int(filtered_df['reposts'].sum()),
            'Total Followers': int(filtered_df['followers'].sum()),
            'Avg. Sentiment': round(filtered_df['sentiment_score'].mean(), 2)
        }

        display_metrics_with_icons(metrics)

        tab1, tab2, = create_tabs()

        with tab1:
            st.plotly_chart(
                create_engagement_scatter(filtered_df),
                use_container_width=True,
                config={
                    'displayModeBar': True,
                    'displaylogo': False,
                    'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    'scrollZoom': True
                }
            )

        with tab2:  # Changed from tab3 to tab2
            col1, col2 = st.columns([0.6, 0.4])
            with col1:
                # Word frequency section
                st.markdown("### Phrase Analysis Settings")

                # Controls in a single row
                control_cols = st.columns([0.6, 0.4])
                with control_cols[0]:
                    word_range = st.slider(
                        "Phrase Length (words)",
                        min_value=2,
                        max_value=8,
                        value=(2, 5),
                        help="Control the minimum and maximum number of words in phrases"
                    )

                with control_cols[1]:
                    include_common = st.checkbox(
                        "Include common terms",
                        value=False,
                        help="Toggle to include/exclude common descriptive terms"
                    )

                # Process text data
                text_data = filtered_df['content'].fillna('').astype(str)
                non_empty_text = [text for text in text_data if text.strip()]

                if non_empty_text:
                    # Create and display chart using improved analysis
                    word_freq_chart = create_word_freq_chart(
                        pd.DataFrame({'content': non_empty_text}),
                        include_common=include_common,
                        min_words=word_range[0],
                        max_words=word_range[1]
                    )
                else:
                    st.warning("No text content available for analysis")
                    word_freq_chart = None

                if word_freq_chart is not None:
                    st.plotly_chart(
                        word_freq_chart,
                        use_container_width=True,
                        config={'displayModeBar': False}
                    )

                # Location chart
                location_counts = get_location_counts(filtered_df)
                st.plotly_chart(
                    create_location_chart(location_counts),
                    use_container_width=True,
                    config={'displayModeBar': False}
                )

            with col2:
                # Sentiment pie chart
                sentiment_counts = filtered_df['sentiment'].value_counts()
                st.plotly_chart(
                    create_pie_chart(sentiment_counts),
                    use_container_width=True,
                    config={'displayModeBar': False}
                )

                # Hashtag frequency chart
                hashtag_freq = get_hashtag_frequency(filtered_df['content'])
                st.plotly_chart(
                    create_hashtag_chart(hashtag_freq),
                    use_container_width=True,
                    config={'displayModeBar': False}
                )

            st.markdown("""
                <h3 style='text-align: center; margin: 2rem 0; 
                font-size: clamp(1.2rem, 1.8vw, 1.8rem);'>📝 Top Viewed Posts</h3>
            """, unsafe_allow_html=True)

            table_df = create_user_table(filtered_df)
            st.dataframe(
                table_df,
                hide_index=True,
                use_container_width=True
            )


    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error(traceback.format_exc())
