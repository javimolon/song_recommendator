import pandas
import time
from tqdm import tqdm
import sys

def get_songs(song):
    return df[df['song_name'] == song]



def common_genres(lst1, lst2): 
    
    return set(lst1) & set(lst2)


def evaluate_similarity(song1,song2):
    
    s = song1.copy()
    del s['song_name']
    for key in s:
        if key == 'playlist':
            genres = common_genres(s[key],song2[key])
            s[key] = -(len(genres)/len(s[key]))*0.3
        elif key == 'artist_name':
            s[key] = -0.15 if s[key] == song2[key] else 0.1
        else:
            s[key] -= song2[key]
            
    for key,value in s.items():
        if key == 'artist_name':
            continue
        s[key] = abs(s[key])
        # key, loudness, mode, speechiness, acousticness
        if key == 'tempo' or key == 'danceability' or key == 'energy' or key == 'instrumentalness' or key == 'audio_valence':
            s[key] = s[key]*2.5
        elif key == 'loudness' or key == 'mode' or key == 'speechiness' or key == 'acousticness': 
            s[key] = s[key]*2
        else:
            s[key] = s[key]*1.2


    
    return sum(s.values())
    


def song_dictionalize(song_name):
    song = df[df['song_name'] == song_name]
    
    song_index = song.index[0]
    
    song = song.to_dict()
    
    for key, value in song.items():
        song[key] = value[song_index]
    return song
  



def get_recommendation(song_name,df: pandas.DataFrame):

    song = song_dictionalize(song_name)
    recommendation = [10e10, '']
    # we create a progress bar
    
    for i in tqdm (range (len(df)), desc="Loading..."):
        try:
            if df['song_name'][i] != song_name:
                song2 = song_dictionalize(df.iloc[i]['song_name'])
                similarity = evaluate_similarity(song, song2)
                
                if similarity < recommendation[0]:
                    recommendation[0] = similarity
                    recommendation[1] = df.iloc[i]['song_name']
        except:
            pass

                   
            
    
    return recommendation[1]

if __name__ == '__main__':
    df1 = pandas.read_csv("song_data.csv")
    df2 = pandas.read_csv("song_info.csv")
    
    df = pandas.merge(df1,df2,on='song_name')
    df.drop_duplicates(subset ="song_name", keep = 'first', inplace = True)
    df.drop(columns=['song_duration_ms','key','audio_mode','time_signature','album_names'],inplace=True)
    
    cols_to_norm = ['speechiness','instrumentalness','liveness','audio_valence','tempo','loudness','danceability','energy','acousticness','song_popularity']
    df[cols_to_norm] = df[cols_to_norm].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    print(df.head())
    

    song_name = input("Enter a song name: ")
    if song_name not in df['song_name'].values:
        print("Song not found")
        sys.exit()
    r = get_recommendation(song_name,df)
    
    print('I suggest you listen to', r, 'by', get_songs(r)['artist_name'].values[0])
    
  

