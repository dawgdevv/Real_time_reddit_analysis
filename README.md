# 🚀 Reddit Real-Time Analytics Dashboard

<div align="center">
  <img src="https://img.shields.io/badge/Built%20With-Dash%20%26%20Plotly-FF5700?style=for-the-badge&logo=plotly" />
  <img src="https://img.shields.io/badge/MongoDB-RealTime%20Data-47A248?style=for-the-badge&logo=mongodb" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</div>

---

## 📈 Project Overview

**Reddit Real-Time Analytics Dashboard** is a dynamic and visually stunning web application that continuously fetches live subreddit data stored in MongoDB and visualizes key insights like:

- 📊 Average Upvotes
- 💬 Average Comments
- 📈 Post Counts
- 😊 Sentiment Trends
- 🔥 Top Subreddits
- 🏆 Highest and Lowest Sentiment Posts

All updated **every 30 seconds**, in **real-time**, without refreshing the page!

> **Built using:**
> - **Dash** (by Plotly) for the interactive dashboard
> - **MongoDB** as the live data source
> - **Plotly Express** for rich, animated graphs
> - **Dash DAQ** for future enhancements (knobs, indicators)
> - **Python** and **Pandas** for data processing

---

## 🎯 Features

- ✅ Real-time Data Refresh (every 30 seconds)
- ✅ Beautiful Dark-Themed UI (Plotly Dark Template)
- ✅ Live Sentiment Tracking Line Graph
- ✅ Post Sentiment Boxplots by Subreddit
- ✅ Top Subreddits Visualization (Pie Chart)
- ✅ Highlighted Highest and Lowest Sentiment Posts
- ✅ Mobile and Desktop Friendly

---

## 🛠️ Tech Stack

| Technology         | Usage                                |
|---------------------|--------------------------------------|
| Dash                | For building reactive, fast dashboards |
| Plotly Express      | For interactive, beautiful plotting |
| MongoDB Atlas       | Cloud-hosted live Reddit data storage |
| Pandas              | Dataframe manipulation and aggregation |
| Python              | Core backend logic |

---

## 📂 Project Structure

```bash
📦 reddit-realtime-dashboard
 ┣ 📜 app.py          # Main Dash app (Dashboard layout, Callbacks, MongoDB integration)
 ┣ 📜 requirements.txt # Python dependencies
 ┗ 📜 README.md        # Project documentation
```

---

## 🔥 Quick Setup & Run Locally

1. **Clone this repository** 🚀

```bash
git clone https://github.com/your-username/reddit-realtime-dashboard.git
cd reddit-realtime-dashboard
```

2. **Install the dependencies** 📦

```bash
pip install -r requirements.txt
```

3. **Run the app** 🖥️

```bash
python app.py
```

4.	Open in Browser 🌐
Navigate to 👉 http://127.0.0.1:8050/ to view your dashboard live!

---

## 🗄️ MongoDB Collections Structure
- subreddit_stats
Contains aggregated statistics for each subreddit:
- subreddit
- avg_upvotes
- avg_comments
- avg_sentiment
- post_count
- processing_timestamp
- reddit_posts
Contains individual post details:
- subreddit
- description
- sentiment_score
- processing_timestamp

Note: Three different MongoDB clients are connected (team collaboration).

---

## 🎨 Dashboard Preview

Upvotes, Comments, and Posts	Sentiment Tracking
	

Top Subreddits	Sentiment Distribution
	

Highlighted Posts


---

## 📌 Future Enhancements
- Add sentiment-based word clouds.
- Introduce filter options (select subreddits, date ranges).
- Add alerts if a subreddit sentiment becomes extremely negative.
- Deploy the app on Render, Heroku, or AWS for public access!

---

## 🤝 Contributors
- Kushagra 
- Dev Verma
- Nishant Raj

---

## ⭐ Show Your Support!

If you like this project, don’t forget to:
- ⭐ Star this repo
- 🍴 Fork it
- 🛠️ Submit PRs
- 🔥 Share with your friends!

---

Built with ❤️ using Python, MongoDB, Dash, and Plotly.

---
