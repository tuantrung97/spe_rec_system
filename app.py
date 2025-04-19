import streamlit as st
import pandas as pd
import os
import gdown

# File paths
USER_RECS_FILE = 'user_recs.csv'
RATINGS_FILE = 'Products_ThoiTrangNam_rating_raw.csv'
SIMILARITY_FILE = '/mnt/data/product_recommendations_1.csv'
BANNER_PATH = 'banner.png'
PLACEHOLDER_IMG = 'logo.jpg'

# Google Drive file IDs (if using Drive downloads)
GDRIVE_FILE_ID_user_rec = '1599V9QJF0fTV3z7gl1XSkJwu0D0GbC2E'
GDRIVE_FILE_ID_ratings = '1o2ipJG4zM3w_57hSLFY9kJbX-YyD-29K'

@st.cache_data
def load_data():
    # Optionally download user_recs and ratings if not present
    if not os.path.exists(USER_RECS_FILE):
        gdown.download(f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_user_rec}', USER_RECS_FILE, quiet=False)
    if not os.path.exists(RATINGS_FILE):
        gdown.download(f'https://drive.google.com/uc?id={GDRIVE_FILE_ID_ratings}', RATINGS_FILE, quiet=False)

    user_recs = pd.read_csv(USER_RECS_FILE, sep='\t', on_bad_lines='skip')
    ratings = pd.read_csv(RATINGS_FILE, sep='\t', on_bad_lines='skip')
    similarity_df = pd.read_csv(SIMILARITY_FILE)
    return user_recs, ratings, similarity_df

# Load data
user_recs, ratings, similarity_df = load_data()

# Top banner
st.image(BANNER_PATH, use_container_width=True)

# Sidebar
st.sidebar.image(PLACEHOLDER_IMG, use_container_width=True)
st.sidebar.markdown("""
# 🎉 Shopee Recommender  
**👨‍💻 By**: Pham Huu Tuan Trung & Tran Nhat Phung  
**📚 Course**: Data Science & Machine Learning @ HCMUS  
""")

# Main app

def main():
    choice = st.sidebar.selectbox("Choose an option", [
        "Recommend products for User",
        "Recommend similar products"
    ])

    if choice == "Recommend similar products":
        st.header("🔍 Recommend Similar Products")

        # Filter choice
        filter_by = st.radio("Filter by", ["Product ID", "Product Name"])
        if filter_by == "Product ID":
            min_id = int(similarity_df['original_product_id'].min())
            max_id = int(similarity_df['original_product_id'].max())
            prod_id = st.number_input(
                "Enter Original Product ID", min_value=min_id, max_value=max_id, step=1
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
            st.markdown(f"### {orig['original_product_name']} (ID: {orig['original_product_id']})")
            try:
                p = float(orig['original_price']); price_str = f"{p:,.0f} VND"
            except:
                price_str = orig['original_price']
            st.write(f"💰 Price: {price_str}")
            st.write(f"⭐ Rating: {orig['original_rating']:.1f}")
            st.markdown(f"[View on Shopee]({orig['original_link']})")

        # Show top 5 similar products
        st.subheader("Top 5 Similar Products")
        sims = (
            df_orig.sort_values('recommendation_rank')
            .head(5)
        )
        for _, row in sims.iterrows():
            cols = st.columns([1, 5])
            with cols[0]:
                img_url = row['recommended_image'] if isinstance(row['recommended_image'], str) and row['recommended_image'] else PLACEHOLDER_IMG
                st.image(img_url, use_container_width=True)
            with cols[1]:
                st.markdown(f"### [{row['recommended_product_name']} (ID: {row['recommended_product_id']})]({row['recommended_link']})")
                try:
                    pr = float(row['recommended_price']); pr_str = f"{pr:,.0f} VND"
                except:
                    pr_str = row['recommended_price']
                st.write(f"💰 Price: {pr_str}")
                st.write(f"📊 Similarity Score: {row['similarity_score']:.3f}")

    else:
        st.header("🛒 Recommend Products for User")
        # --- existing user recommendation code remains unchanged ---

if __name__ == "__main__":
    main()
