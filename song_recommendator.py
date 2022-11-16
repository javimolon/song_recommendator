import pandas
import time
from tqdm import tqdm
import os, sys, signal
import numpy as np
import re
import xml.etree.ElementTree as ET

def handle_exit(signal, frame):
    print('Exiting', end='', flush=True)
    for _ in range(5):

        print('.', end='', flush=True)
        time.sleep(0.15)
    sys.exit(0)
signal.signal(signal.SIGINT, handle_exit)

def get_songs(song):
    return df[df['song_name'] == song]

def dtypes():
    types = {'object': 'str', 'int64': 'int', 'float64': 'float', 'datetime64[ns]': 'datetime'}
    df_list = extract()
    df_names = ['song_data.csv', 'song_info.csv']
    file = ET.Element('recomendator')
    
    for dataset in range(len(df_list)):
        csv = ET.SubElement(file, 'csv')
        for col in df_list[dataset].columns:
            ET.SubElement(csv, 'columns', attrib={'name': col, 'type': types[str(df_list[dataset][col].dtype)]})
       
    
    return file

def evaluate_similarity(song1: dict,song2: dict):
    s = song1.copy()
    del s['song_name']
    for key in s:
        if key == 'playlist':
            if re.match(song2[key],s[key]):
                s[key] = 0
            else:
                s[key] = 0.2
        elif key == 'artist_name':
            if re.match(song2[key],s[key]):
                s[key] = 0
            else:
                s[key] = 0.6
            
        else:
            s[key] -= song2[key]
            
    for key in s.keys():
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
  
def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

def search_song(df, song_name):
    menores = {'1':1000,'2':1000,'3':1000,'4':1000,'5':1000}
    print('Looking for your song...')
    for i in tqdm (range (len(df)), desc="Loading..."):
        if re.match(song_name,df['song_name'][i].lower()):
            d = 0
        else:
            d = levenshtein(song_name, df['song_name'][i])
        
        for m, val in menores.items():
            if d < val:
                menores[df['song_name'][i]] = d
                menores.pop(m)
                break
    menores = {k: v for k, v in sorted(menores.items(), key=lambda item: item[1])}
    return menores

def get_recommendation(song_name,df: pandas.DataFrame):
    song = song_dictionalize(song_name)
    recommendation = [10e10, '']
    # we create a progress bar
    print('Searching for similar songs...')
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

def extract():
    df1 = pandas.read_csv("song_data.csv")
    df2 = pandas.read_csv("song_info.csv")
    return df1, df2

def transform(df1: pandas.DataFrame, df2: pandas.DataFrame):
    df = pandas.merge(df1,df2,on='song_name')
    df.drop_duplicates(subset ="song_name", keep = 'first', inplace = True)
    df = df.reset_index(drop=True)
    df.drop(columns=['song_duration_ms','key','audio_mode','time_signature','album_names'],inplace=True)
    
    cols_to_norm = ['speechiness','instrumentalness','liveness','audio_valence','tempo','loudness','danceability','energy','acousticness','song_popularity']
    df[cols_to_norm] = df[cols_to_norm].apply(lambda x: (x - x.min()) / (x.max() - x.min()))
    return df

def load(df):
    df.to_csv('resources_created/song_data.csv',index=False)
    file = dtypes()
    new_f =  open('resources_created/dtypes.xml', 'w')
    new_f.write(ET.tostring(file, encoding='unicode')) 
    new_f.close()

if __name__ == '__main__':
    df1, df2 = extract()
    df = transform(df1, df2)
    load(df)
    
    # Interactive mode
    os.system('cls||clear')
    song_name = input("Enter a song name: ")
    
    if song_name not in df['song_name'].values:

        similar = search_song(df, song_name)
        first_name = list(similar.keys())[0]
        a = ''
        while a != 'y' and a != 'n':
            print('We didn\'t find your song in our data, do you mean',first_name, 'by', get_songs(first_name)['artist_name'].values[0],'(y/n)?')
            a = input('')
            if a == 'y':
                song_name = first_name
                break
            if a == 'n':
                similar.pop(first_name)
                count = 1
                for key in list(similar.keys()):
                    print(str(count)+'.', key, 'by', get_songs(key)['artist_name'].values[0],'\n')
                    count += 1
                b = ''
                while b != 'y' and b != 'n':
                    b = input('Is one of these the song you were looking for (y/n)?')
                    if b == 'y':
                        song_number = ''
                        while song_number not in list(range(1,len(similar.keys())+1)):
                            try:
                                song_number = int(input('Which one? '))
                            except:
                                print('Please enter a number')
                                continue
                            
                           
                        song_name = list(similar.keys())[song_number-1]
                    elif b == 'n':
                        print('Sorry, we couldn\'t find your song')
                        sys.exit()
                    else:
                        print('Please enter a valid option')
                        continue
                

        
    r = get_recommendation(song_name,df)
    
    print('I suggest you listen to', r, 'by', get_songs(r)['artist_name'].values[0])
    
  

