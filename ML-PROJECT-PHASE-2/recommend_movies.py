import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
from sklearn.preprocessing import OrdinalEncoder

movies = pd.read_csv('movies.csv')
tags = pd.read_csv('tags.csv')
ratings = pd.read_csv('ratings.csv')

#creating the necessary dataframe
df = pd.merge(movies, tags, on='movieId')
df = pd.merge(df, ratings, on=['userId','movieId'])
df['genres'] = df.apply(lambda x: x['genres'].split('|'),axis=1)
df['Year'] = df['title'].str.extract('.*\((.*)\).*',expand = False)
#creating another dataframe with pop movies coming first, sorted based on mean ratings and no.of user revies
mean_ratings = ratings.groupby('movieId').rating.mean()
num_users = ratings.groupby('movieId').userId.count()
mean_ratings_mov_temp = pd.merge(mean_ratings, movies, how='inner', on='movieId')
mean_ratings_mov = pd.merge(mean_ratings_mov_temp, num_users, how='inner', on='movieId')
mean_ratings_mov.drop(columns='genres', inplace=True)
mean_ratings_mov.rename(columns={'rating':'mean_ratings','userId':'num_users'}, inplace=True)
pop_movs = mean_ratings_mov[mean_ratings_mov["num_users"]>100].sort_values('mean_ratings',ascending=False)
#Using Ordinal encoder and adding two new columns which specify the encodings of user_id and movie_id
encoder = OrdinalEncoder()
df['user_id_encoding'] = encoder.fit_transform(df['userId'].values.reshape((-1, 1))).astype(int).reshape(-1)
df['movie_id_encoding'] =  encoder.fit_transform(df['movieId'].values.reshape((-1, 1))).astype(int).reshape(-1)
X = csr_matrix((df.rating, (df.user_id_encoding, df.movie_id_encoding)))


W = cosine_similarity(X.T, X.T) #cosine similarity matrix

ranked_results = {
    movie_id: np.argsort(similarities)[::-1]
    for movie_id, similarities in enumerate(W)
}

def recommendations(movie_title, n):
    movie_id = movies.set_index('title').loc[movie_title][0]
    movie_csr_id = encoder.transform([[movie_id]])[0, 0].astype(int)
    rankings = ranked_results[movie_csr_id][:n]
    ranked_indices = encoder.inverse_transform(rankings.reshape((-1, 1))).reshape(-1)
    return movies.set_index('movieId').loc[ranked_indices]

def recommend(keyword):
    if len(return_movies(keyword)) >0:
        return recommendations(return_movies(keyword)[0],10)
    else:
        print("No recommended movies")
        
def strip_char(list):
    for i in range(len(list)):
        list[i] = list[i].lower().strip(":;,.''[]}{)(*&^%$#@!|")
    return list

def top_movies(number_of_movies):
    df = pop_movs.head(number_of_movies)
    return df
new_df = pd.DataFrame()
new_df['title'] = df['title']
new_df['movieId'] = df['movieId']
new_df['genres'] = df['genres']
new_df['keywords'] = df.apply(lambda x: [x['tag'],x['Year']], axis=1)
new_df.apply(lambda x: x['keywords'].extend(x['title'].split(' ')),axis=1)
new_df.apply(lambda x: x['keywords'].extend(x['genres']),axis=1)
new_df.drop('genres',inplace=True,axis=1)
for i in new_df['keywords']:
    try:
        i = strip_char(i)
    except:
        pass
    
def return_movies(keyword):
    movie_names = []
    name_token = keyword.split(' ')
    for i in range(new_df.shape[0]):
        for j in range(len(name_token)):
            if name_token[j].lower().strip(":;,.''[]}{)(*&^%$#@!|") in new_df.loc[i,"keywords"]:
                movie_names.append(new_df.loc[i,"title"])
    result = list(dict.fromkeys(movie_names))
    return result

recommend('toy story')