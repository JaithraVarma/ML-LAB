from fastapi import FastAPI, Path
import recommend
import requests
import ast
app = FastAPI()

@app.get('/recommendations')
def recommend_movie(keyword):
    df = recommend.recommend(keyword)
    return df

@app.get('/popular movies/{number of movies}')
def pop_movies(num_movies: int = Path(title="Number of Popular Movies")):
    df = recommend.pop_movies(num_movies)
    result = df['title'].to_list()
    return result

@app.get('/images/{tmdb Id}')
def grab_poster(tmdbId: int = Path(title="tmdbId for the movie")):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=621d3fee8614662e39e4cfea30a2a3ba&language=en-US'.format(tmdbId))
    data = response.content
    data = data.decode('UTF-8')
    data = data.replace('false','False')
    data = ast.literal_eval(data)
    return 'https://image.tmdb.org/t/p/w500/{}'.format(data['poster_path'])

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8443)