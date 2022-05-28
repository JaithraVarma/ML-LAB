from fastapi import FastAPI, Path
import recommend_movies
import requests
import ast
app = FastAPI()

@app.get('/recommendations')
def recommend_movie(keyword):
    df = recommend_movies.recommend(keyword)
    return df

@app.get('/popular movies/{number of movies}')
def pop_movies(num_movies: int = Path(title="Number of Popular Movies")):
    df = recommend_movies.top_movies(num_movies)
    result = df['title'].to_list()
    return result

@app.get('/images/{tmdb Id}')
def grab_poster(tmdbId: int = Path(title="tmdbId for the movie")):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=a90f768899e05006263dd44ef602929e&language=en-US'.format(tmdbId))
    data = response.content
    data = data.decode('UTF-8')
    data = data.replace('false','False')
    data = ast.literal_eval(data)
    return 'https://image.tmdb.org/t/p/w500/{}'.format(data['poster_path'])

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=80)