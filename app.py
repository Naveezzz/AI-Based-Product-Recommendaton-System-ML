from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
from scipy.sparse.linalg import svds
from scipy.sparse import csr_matrix

app = Flask(__name__)

# Load and preprocess data (You need to have 'ratings_Electronics.csv' in the same directory)
df = pd.read_csv('ratings_Electronics.csv', header=None)
df.columns = ['user_id', 'prod_id', 'rating', 'timestamp']
df = df.drop('timestamp', axis=1)

# Create the interaction matrix
df_copy = df.copy(deep=True)
counts = df['user_id'].value_counts()
df_final = df[df['user_id'].isin(counts[counts >= 50].index)]
final_ratings_matrix = df_final.pivot(index='user_id', columns='prod_id', values='rating').fillna(0)
final_ratings_sparse = csr_matrix(final_ratings_matrix.values)

# Singular Value Decomposition
U, s, Vt = svds(final_ratings_sparse, k=50)
sigma = np.diag(s)
all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt)
preds_df = pd.DataFrame(abs(all_user_predicted_ratings), columns=final_ratings_matrix.columns)
preds_matrix = csr_matrix(preds_df.values)

# Common Recommendation Logic (Sample Logic)
def get_common_recommendations(num_recommendations):
    common_recommendations = []

    # Count the number of users who have rated each product
    product_rated_counts = df_final['prod_id'].value_counts()

    # Filter for products with at least 50 ratings
    popular_products = product_rated_counts[product_rated_counts >= 50].index

    # Find the products with the highest average rating among popular products
    product_avg_ratings = df_final.groupby('prod_id')['rating'].mean()
    top_rated_products = product_avg_ratings[popular_products].sort_values(ascending=False)

    # Get the top common recommendations
    common_recommendations = top_rated_products.head(num_recommendations).index.tolist()

    return common_recommendations

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    user_index = int(request.form.get('user_index'))
    num_recommendations = int(request.form.get('num_recommendations'))

    user_ratings = final_ratings_sparse[user_index, :].toarray().reshape(-1)
    user_predictions = preds_matrix[user_index, :].toarray().reshape(-1)
    temp = pd.DataFrame({'user_ratings': user_ratings, 'user_predictions': user_predictions})
    temp['Recommended Products'] = final_ratings_matrix.columns
    temp = temp.set_index('Recommended Products')
    temp = temp.loc[temp.user_ratings == 0]
    temp = temp.sort_values('user_predictions', ascending=False)

    recommendations = temp.head(num_recommendations).index.tolist()

    return jsonify({"recommendations": recommendations})

@app.route('/common_recommendations', methods=['POST'])
def common_recommendations():
    num_common_recommendations = int(request.form.get('num_common_recommendations'))

    common_recommendations = get_common_recommendations(num_common_recommendations)

    return jsonify({"common_recommendations": common_recommendations})

if __name__ == '__main__':
    app.run(debug=True)
