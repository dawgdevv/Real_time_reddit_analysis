import dash_daq as daq
from dash import dcc, html, Output, Input, dcc, html, dash_table
import plotly.io as pio
import dash
# Set global Plotly template
pio.templates.default = "plotly_dark"

from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pymongo import MongoClient
import datetime
import os
load_dotenv()

# MongoDB Clients for all three team members
client_1 = MongoClient(os.getenv("MONGO_URI_1"))
client_2 = MongoClient(os.getenv("MONGO_URI_2"))
client_3 = MongoClient(os.getenv("MONGO_URI_3"))
# Database and collections for each client
db_1 = client_1['reddit_analytics']
collection_1 = db_1['subreddit_stats']
posts_collection_1 = db_1['reddit_posts']

db_2 = client_2['reddit_analytics']
collection_2 = db_2['subreddit_stats']
posts_collection_2 = db_2['reddit_posts']

db_3 = client_3['reddit_analytics']
collection_3 = db_3['subreddit_stats']
posts_collection_3 = db_3['reddit_posts']

# Dash App Setup
app = dash.Dash(__name__)
server = app.server

# Layout
# Layout
app.layout = html.Div(
    style={
        'backgroundColor': '#181818',
        'fontFamily': 'Segoe UI, Arial, sans-serif',
        'color': '#EEEEEE',
        'padding': '20px'
    },
    children=[
        html.H1("Reddit Real-Time Analytics Dashboard", 
                style={'textAlign': 'center', 'marginBottom': '40px', 'fontWeight': 'bold', 'fontSize': '38px', 'color': '#FF5700'}),

        html.Div([
            dcc.Graph(id='upvote-bar-plot', style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)'}),
            dcc.Graph(id='downvote-bar-plot', style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)'}),
            dcc.Graph(id='comments-bar-plot', style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)'}),
        ], style={'display': 'grid', 'gridTemplateColumns': '1fr', 'gap': '25px', 'marginBottom': '40px'}),

        dcc.Graph(id='sentiment-line-plot', 
                  style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)', 'height': '50vh', 'marginBottom': '40px'}),

        html.Div([
            dcc.Graph(id='top-subreddits-pie', style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)'}),
            dcc.Graph(id='sentiment-boxplot', style={'borderRadius': '12px', 'boxShadow': '0 4px 12px rgba(0,0,0,0.7)'})
        ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '25px', 'marginBottom': '40px'}),

        html.Div([
            html.Div([
                html.H3("🔥 Highest Sentiment Post", style={'textAlign': 'center', 'marginBottom': '10px', 'color': '#00FFB3'}),
                html.Div(id='highest-sentiment-post', style={
                    'padding': '18px', 'backgroundColor': '#23272F', 'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.7)', 'fontSize': '17px', 'minHeight': '120px'
                })
            ], style={'marginBottom': '30px'}),

            html.Div([
                html.H3("❄️ Lowest Sentiment Post", style={'textAlign': 'center', 'marginBottom': '10px', 'color': '#FF4B4B'}),
                html.Div(id='lowest-sentiment-post', style={
                    'padding': '18px', 'backgroundColor': '#23272F', 'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.7)', 'fontSize': '17px', 'minHeight': '120px'
                })
            ])
        ], style={'maxWidth': '900px', 'margin': 'auto'})
    ]
)

# Refresh interval (set to 30 seconds)
app.layout.children.append(
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  
        n_intervals=0
    )
)

# Callbacks
@app.callback(
    [Output('upvote-bar-plot', 'figure'),
    Output('downvote-bar-plot', 'figure'),
    Output('comments-bar-plot', 'figure'),
    Output('sentiment-line-plot', 'figure'),
    Output('top-subreddits-pie', 'figure'),
    Output('sentiment-boxplot', 'figure'),
    Output('highest-sentiment-post', 'children'),
    Output('lowest-sentiment-post', 'children')],
    Input('interval-component', 'n_intervals')
)
def update_graphs(n):
    try:
        # Fetch data from all three MongoDB clients
        data_1 = list(collection_1.find({}))
        posts_data_1 = list(posts_collection_1.find({}))
        
        data_2 = list(collection_2.find({}))
        posts_data_2 = list(posts_collection_2.find({}))
        
        data_3 = list(collection_3.find({}))
        posts_data_3 = list(posts_collection_3.find({}))

        if not data_1 or not data_2 or not data_3 or not posts_data_1 or not posts_data_2 or not posts_data_3:
            raise Exception("MongoDB returned nothing.")

        # Merge data from all clients
        all_data = data_1 + data_2 + data_3
        all_posts_data = posts_data_1 + posts_data_2 + posts_data_3

        df = pd.DataFrame(all_data)
        posts_df = pd.DataFrame(all_posts_data)

        # Convert to datetime
        df['processing_timestamp'] = pd.to_datetime(df.get('processing_timestamp', datetime.datetime.now()))
        posts_df['processing_timestamp'] = pd.to_datetime(posts_df.get('processing_timestamp', datetime.datetime.now()))

        # Your existing plot code for updating the graphs
        color_seq = px.colors.sequential.Viridis

        upvote_fig = px.bar(
            df, x='subreddit', y='avg_upvotes', color='subreddit',
            color_discrete_sequence=color_seq,
            title='Average Upvotes Per Subreddit'
        )
        upvote_fig.update_layout(
            xaxis_title="Subreddit", yaxis_title="Average Upvotes",
            title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818'
        )

        downvote_fig = px.bar(
            df, x='subreddit', y='avg_comments', color='subreddit',
            color_discrete_sequence=color_seq,
            title='Average Comments Per Subreddit'
        )
        downvote_fig.update_layout(
            xaxis_title="Subreddit", yaxis_title="Average Comments",
            title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818'
        )

        comments_fig = px.bar(
            df, x='subreddit', y='post_count', color='subreddit',
            color_discrete_sequence=color_seq,
            title='Number of Posts Per Subreddit'
        )
        comments_fig.update_layout(
            xaxis_title="Subreddit", yaxis_title="Number of Posts",
            title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818'
        )

        sentiment_fig = px.line(
            df, x="processing_timestamp", y="avg_sentiment", color="subreddit",
            color_discrete_sequence=color_seq,
            title="Real-Time Sentiment Tracking", markers=True
        )
        sentiment_fig.update_layout(
            xaxis_title="Time", yaxis_title="Average Sentiment",
            title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818'
        )

        top_subs = df.nlargest(5, 'post_count')
        pie_fig = px.pie(
            top_subs, values='post_count', names='subreddit',
            color_discrete_sequence=px.colors.sequential.Plasma,
            title='Top 5 Subreddits by Post Count'
        )
        pie_fig.update_layout(title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818')

        sentiment_box_fig = px.box(
            posts_df, x="subreddit", y="sentiment_score",
            color="subreddit", color_discrete_sequence=color_seq,
            title="Sentiment Distribution per Subreddit"
        )
        sentiment_box_fig.update_layout(
            xaxis_title="Subreddit", yaxis_title="Sentiment Score",
            title_font_size=22, plot_bgcolor='#181818', paper_bgcolor='#181818'
        )

        # Format post details with Markdown and highlight sentiment
        highest_post = posts_df.loc[posts_df['sentiment_score'].idxmax()]
        lowest_post = posts_df.loc[posts_df['sentiment_score'].idxmin()]

        highest_sentiment_text = dcc.Markdown(
            f"**Subreddit:** `{highest_post['subreddit']}`  \n"
            f"**Sentiment Score:** <span style='color:#00FFB3;font-weight:bold'>{highest_post['sentiment_score']:.2f}</span>  \n"
            f"**Description:** {highest_post.get('description', '')[:300]}...",
            dangerously_allow_html=True
        )
        lowest_sentiment_text = dcc.Markdown(
            f"**Subreddit:** `{lowest_post['subreddit']}`  \n"
            f"**Sentiment Score:** <span style='color:#FF4B4B;font-weight:bold'>{lowest_post['sentiment_score']:.2f}</span>  \n"
            f"**Description:** {lowest_post.get('description', '')[:300]}...",
            dangerously_allow_html=True
        )

        return upvote_fig, downvote_fig, comments_fig, sentiment_fig, pie_fig, sentiment_box_fig, highest_sentiment_text, lowest_sentiment_text

    except Exception as e:
        print(f"Dashboard Error: {e}")
        empty_fig = go.Figure()
        empty_fig.update_layout(title="No Data Available")
        return empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, "No Data", "No Data"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
