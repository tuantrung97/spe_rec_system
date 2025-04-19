import streamlit as st
import pandas as pd
import os
import gdown

# File paths
USER_RECS_FILE = 'user_recs.csv'
RATINGS_FILE = 'Products_ThoiTrangNam_rating_raw.csv'
SIMILARITY_FILE = 'product_recommendations_1.csv'
BANNER_PATH = 'banner.png'
PLACEHOLDER_IMG = 'logo.jpg'

# Google Drive file IDs
GDRIVE_FILE_ID_user_rec = '1599V9QJF0fTV3z7gl1XSkJwu0D0GbC2E'
GDRIVE_FILE_ID_ratings = '1o2ipJG4zM3w_57hSLFY9kJbX-YyD-29K'

@st.cache_data
def load_data():
    # Download user_recs.csv if not present
    if not os.path.exists(USER_RECS_FILE):
        gdown.download(
            f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_user_rec}',
            USER_RECS_FILE,
            quiet=False
        )
    # Download ratings if not present
    if not os.path.exists(RATINGS_FILE):
        gdown.download(
            f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_ratings}',
            RATINGS_FILE,
            quiet=False
        )

    user_recs = pd.read_csv(USER_RECS_FILE, sep='\t', on_bad_lines='skip')
    ratings = pd.read_csv(RATINGS_FILE, sep='\t', on_bad_lines='skip')
    similarity_df = pd.read_csv(SIMILARITY_FILE)
    return user_recs, ratings, similarity_df

# Load data
user_recs, ratings, similarity_df = load_data()

# UI – Top banner
st.image(BANNER_PATH, use_container_width=True)

# Sidebar
st.sidebar.image(PLACEHOLDER_IMG, use_container_width=True)
st.sidebar.markdown("""
# 🎉 Shopee Recommender  
**👨‍💻 By**: Pham Huu Tuan Trung & Tran Nhat Phung  
**📚 Course**: Data Science & Machine Learning @ HCMUS  
**🔍 Purpose**: Explore personalized product recommendations with:
- 🧠 Gensim content-based similarity
- 🤝 ALS collaborative filtering
""")

# Main app function
def main():
    choice = st.sidebar.selectbox(
        "Choose an option", 
        ["Recommend products for User", "Recommend similar products"]
    )

    if choice == "Recommend similar products":
        st.header("🔍 Recommend Similar Products")

        # Filter choice
        filter_by = st.radio("Filter by", ["Product ID", "Product Name"])
        if filter_by == "Product ID":
            min_id = int(similarity_df['original_product_id'].min())
            max_id = int(similarity_df['original_product_id'].max())
            prod_id = st.number_input(
                "Enter Original Product ID", 
                min_value=min_id, max_value=max_id, step=1
            )
            df_orig = similarity_df[similarity_df['original_product_id'] == prod_id]
            if df_orig.empty:
                st.warning("Product ID not found.")
                return
            prod_name = df_orig['original_product_name'].iloc[0]
        else:
            names = sorted(similarity_df['original_product_name'].unique())
            prod_name = st.selectbox("Select Original Product Name", names)
            df_orig = similarity_df[similarity_df['original_product_name'] == prod_name]
            prod_id = int(df_orig['original_product_id'].iloc[0])

        # Display selected original product
        st.subheader("Selected Product")
        orig = df_orig.iloc[0]
        cols = st.columns([1, 4])
        with cols[0]:
            img = orig['original_image'] if isinstance(orig['original_image'], str) and orig['original_image'] else PLACEHOLDER_IMG
            st.image(img, use_container_width=True)
        with cols[1]:
            st.markdown(
                f"### {orig['original_product_name']} (ID: {orig['original_product_id']})"
            )
            try:
                p = float(orig['original_price'])
                price_str = f"{p:,.0f} VND"
            except:
                price_str = orig['original_price']
            st.write(f"💰 Price: {price_str}")
            st.write(f"⭐ Rating: {orig['original_rating']:.1f}")
            st.markdown(f"[View on Shopee]({orig['original_link']})")

        # Show top 5 similar products
        st.subheader("Top 5 Similar Products")
        sims = df_orig.sort_values('recommendation_rank').head(5)
        for _, row in sims.iterrows():
            cols = st.columns([1, 5])
            with cols[0]:
                img_url = row['recommended_image'] if isinstance(row['recommended_image'], str) and row['recommended_image'] else PLACEHOLDER_IMG
                st.image(img_url, use_container_width=True)
            with cols[1]:
                st.markdown(
                    f"### [{row['recommended_product_name']} (ID: {row['recommended_product_id']})]({row['recommended_link']})"
                )
                try:
                    pr = float(row['recommended_price'])
                    pr_str = f"{pr:,.0f} VND"
                except:
                    pr_str = row['recommended_price']
                st.write(f"💰 Price: {pr_str}")
                st.write(f"📊 Similarity Score: {row['similarity_score']:.3f}")

    else:
        st.header("🛒 Recommend Products for User")

        # Show sample of 10 random customers (no index)
        unique_users = ratings[['user_id', 'user']].drop_duplicates()
        sample_users = unique_users.sample(10, random_state=42).reset_index(drop=True)
        st.subheader("Sample Customers")
        st.table(sample_users.to_dict('records'))

        # User ID input field
        min_id = int(unique_users['user_id'].min())
        max_id = int(unique_users['user_id'].max())
        user_id = st.number_input(
            "Enter User ID for Recommendations", 
            min_value=min_id, max_value=max_id, value=min_id, step=1
        )

        # Display user's name
        user_row = unique_users[unique_users['user_id'] == user_id]
        user_name = user_row['user'].values[0] if not user_row.empty else "Unknown"

        # Fetch top 5 recommendations for the selected user
        recs = (
            user_recs[user_recs['user_id'] == user_id]
            .sort_values('rating', ascending=False)
            .head(5)
        )

        st.subheader(f"Top 5 Recommendations for {user_name} (ID: {user_id})")
        for _, row in recs.iterrows():
            cols = st.columns([1, 5])
            img_url = row['image'] if isinstance(row['image'], str) and row['image'] else PLACEHOLDER_IMG
            with cols[0]:
                st.image(img_url, use_container_width=True)
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
