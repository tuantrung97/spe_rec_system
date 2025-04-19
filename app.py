import streamlit as st
import pandas as pd
import os
import gdown

# File paths
USER_RECS_FILE = 'user_recs.csv'
RATINGS_FILE = 'Products_ThoiTrangNam_rating_raw.csv'
BANNER_PATH = 'banner.png'
PLACEHOLDER_IMG = 'logo.jpg'

# Google Drive file ID (replace with your actual ID)
GDRIVE_FILE_ID_user_rec = '1599V9QJF0fTV3z7gl1XSkJwu0D0GbC2E'
GDRIVE_FILE_ID_ratings = '1o2ipJG4zM3w_57hSLFY9kJbX-YyD-29K'

@st.cache_data
def load_data():
    # Download user_recs.csv if not present
    if not os.path.exists(USER_RECS_FILE):
        gdown.download(f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_user_rec}', USER_RECS_FILE, quiet=False)
    if not os.path.exists(RATINGS_FILE):
        gdown.download(f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_ratings}', RATINGS_FILE, quiet=False)
        
    user_recs = pd.read_csv(USER_RECS_FILE, sep='\t', on_bad_lines='skip')
    ratings = pd.read_csv(RATINGS_FILE, sep='\t', on_bad_lines='skip')
    return user_recs, ratings

# Load data
user_recs, ratings = load_data()

# UI – Top banner
st.image(BANNER_PATH, use_container_width=True)

# Sidebar
st.sidebar.image(PLACEHOLDER_IMG, use_container_width=True)
st.sidebar.markdown("""
# 🎉 Shopee Recommender  
**👨‍💻 By**: Pham Huu Tuan Trung & Tran Nhat Phung  
**📚 Course**: Data Science & Machine Learning @ HCMUS  
**🔍 Purpose**: Explore personalized product recommendations using:
- 🧠 Content-based (Gensim)
- 🤝 Collaborative Filtering (ALS)
""")

# Main app
def main():
    choice = st.sidebar.selectbox("Choose an option", [
        "Recommend products for User", 
        "Recommend similar products"
    ])

    if choice == "Recommend similar products":
        st.header("🔍 Recommend Similar Products")
        st.write("To be updated")
    else:
        st.header("🛒 Recommend Products for User")

        # Sample users table (no index)
        unique_users = ratings[['user_id', 'user']].drop_duplicates()
        sample_users = unique_users.sample(10, random_state=42).reset_index(drop=True)
        st.subheader("Sample Customers")
        st.table(sample_users.to_dict('records'))

        # User ID input
        min_id = int(unique_users['user_id'].min())
        max_id = int(unique_users['user_id'].max())
        user_id = st.number_input(
            "Enter User ID for Recommendations", 
            min_value=min_id, max_value=max_id, value=min_id, step=1
        )

        # Display user's name
        user_row = unique_users[unique_users['user_id'] == user_id]
        user_name = user_row['user'].values[0] if not user_row.empty else "Unknown"

        # Get recommendations
        recs = (
            user_recs[user_recs['user_id'] == user_id]
            .sort_values('rating', ascending=False)
            .head(5)
        )

        st.subheader(f"Top 5 Recommendations for {user_name} (ID: {user_id})")

        for _, row in recs.iterrows():
            cols = st.columns([1, 5])
            img_url = row['image'] if isinstance(row['image'], str) and row['image'] else None
            with cols[0]:
                st.image(img_url if img_url else PLACEHOLDER_IMG, use_container_width=True)
            with cols[1]:
                try:
                    price_val = float(row['price'])
                    price_str = f"{price_val:,.0f} VND"
                except:
                    price_str = row['price']
                st.markdown(f"### [{row['product_name']}]({row['link']})")
                st.write(f"💰 Price: {price_str}")
                st.write(f"⭐ Predicted rating: {row['rating']:.2f}")

if __name__ == "__main__":
    main()
