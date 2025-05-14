import csv
import re
import os
from datetime import timedelta
from dataclasses import dataclass
import pathlib

@dataclass
class SongDto:
    artist: str
    track: str
    album: str
    spotify_uri: str
    duration_ms: int
    spotify_url: str
    youtube_url: str
    stream: int
    likes: int = 0
    views: int = 0

def convert_duration(ms: int) -> str:
    """Convert duration from milliseconds to HH:MM:SS format"""
    seconds = int(float(ms)) // 1000
    return str(timedelta(seconds=seconds))

def parse_csv() -> list:
    songs = []
    try:
        file_path = pathlib.Path(__file__).parent.absolute() / "music.csv"
        print(f"Intentando abrir archivo: {file_path}")
        
        with open(file_path, 'r', encoding='latin-1') as file:
            # Usar coma como delimitador explícitamente
            csv_reader = csv.DictReader(file, delimiter=',')
            
            if not csv_reader.fieldnames:
                print("Error: El archivo no tiene encabezados")
                return []
                
            #print(f"Columnas encontradas: {csv_reader.fieldnames}")
            
            for row in csv_reader:
                try:
                    # Verificar que row sea un diccionario válido
                    if not isinstance(row, dict):
                        print(f"Error: Fila no es un diccionario: {row}")
                        continue
                        
                    # Extraer valores con manejo seguro
                    artist = row.get('Artist', '') if row.get('Artist') else ''
                    if isinstance(artist, str):
                        artist = artist.strip()
                    else:
                        artist = str(artist)
                    
                    track = row.get('Track', '') if row.get('Track') else ''
                    if isinstance(track, str):
                        track = track.strip()
                    else:
                        track = str(track)
                    
                    # Obtener duración de manera segura
                    duration = row.get('Duration_ms') or row.get('Duration', '0')
                    if duration is None or duration == '':
                        duration = '0'
                    
                    # Crear el objeto SongDto con valores seguros
                    song = SongDto(
                        artist=artist,
                        track=track,
                        album=str(row.get('Album', '')).strip(),
                        spotify_uri=str(row.get('Uri', '')).strip(),
                        duration_ms=int(float(duration)),
                        spotify_url=str(row.get('Url_spotify', '')).strip(),
                        youtube_url=str(row.get('Url_youtube', '')).strip(),
                        stream=int(float(row.get('Stream', '0') or '0')),
                        likes=int(float(row.get('Likes', '0') or '0')),
                        views=int(float(row.get('Views', '0') or '0'))
                    )
                    songs.append(song)
                except (ValueError, KeyError, TypeError) as e:
                    # print(f"Error procesando fila: {e}")
                    # print(f"Contenido de la fila: {row}")
                    continue
                    
            print(f"Se cargaron {len(songs)} canciones")
            return songs
    except FileNotFoundError:
        print(f"Archivo music.csv no encontrado en {file_path}")
        return []
    except Exception as e:
        print(f"Error general: {e}")
        return []
    
def search_songs() -> None:
    songs = parse_csv()
    
    print("\nEnter search term for title or artist (press Enter with no text to exit):")
    while True:
        search_term = input("> ").strip()
        
        if not search_term:
            break
            
        # Search using case-insensitive comparison for better reliability
        matches = [
            song for song in songs 
            if search_term.lower() in song.artist.lower() or search_term.lower() in song.track.lower()
        ]
        
        # Sort by views count (descending) if available, otherwise by stream
        matches.sort(key=lambda x: (x.views if x.views > 0 else x.stream), reverse=True)
        
        if matches:
            print(f"\nSe encontraron {len(matches)} coincidencias:")
            for song in matches:
                duration = convert_duration(song.duration_ms)
                print(f"Artista: {song.artist}")
                print(f"Canción: {song.track}")
                print(f"Duración: {duration}")
                if song.views > 0:
                    views_m = song.views / 1_000_000
                    print(f"Reproducciones: {views_m:.1f}M vistas")
                elif song.stream > 0:
                    stream_m = song.stream / 1_000_000
                    print(f"Reproducciones: {stream_m:.1f}M streams")
                print("-" * 50)
        else:
            print("No se encontraron coincidencias.")

def artist_top_songs() -> None:
    songs = parse_csv()
    
    artist_name = input("\nEnter artist name: ").strip()

    artist_songs = [song for song in songs if artist_name.lower() in song.artist.lower()]
    
    # Sort by stream count (descending)
    artist_songs.sort(key=lambda x: (x.views if x.views > 0 else x.stream), reverse=True)
    
    # Get top 10 songs
    top_songs = artist_songs[:10]
    
    if top_songs:
        print(f"\nTop 10 songs by {artist_name}:")
        for i, song in enumerate(top_songs, 1):
            print(f"\nTop {i}:")
            print(f"Artist: {song.artist}")
            print(f"Duration: {convert_duration(song.duration_ms)}")
            if song.views > 0:
                views_m = song.views / 1_000_000
                print(f"Reproducciones: {views_m:.1f}M vistas")
            elif song.stream > 0:
                stream_m = song.stream / 1_000_000
                print(f"Reproducciones: {stream_m:.1f}M streams")
            print("-" * 50)
    else:
        print(f"No songs found for artist '{artist_name}'.")

def validate_song_data(data: dict) -> bool:
    """Validate song data using regex patterns"""
    # Basic validation patterns
    patterns = {
        'artist': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'track': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'album': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'spotify_uri': r'^spotify:track:[a-zA-Z0-9]{22}$',
        'duration_ms': r'^\d+$',
        'spotify_url': r'^https://open\.spotify\.com/artist/[a-zA-Z0-9]{22}(\?si=[a-zA-Z0-9]+)?$',
        'youtube_url': r'^https://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_\-]{11}.*$',
        'likes': r'^\d+(\.\d+)?$',
        'views': r'^\d+(\.\d+)?$'
    }
    
    for field, pattern in patterns.items():
        if field in data and data[field]:
            if not re.match(pattern, str(data[field])):
                print(f"Invalid format for {field}: {data[field]}")
                return False
    
    # Validate likes shouldn't be more than views
    if 'likes' in data and 'views' in data:
        if int(data['likes']) > int(data['views']):
            print("Error: Likes cannot be more than views.")
            return False
            
    return True

def insert_song_manual() -> None:
    """Insert a song manually from terminal input"""
    print("\nInsert new song data:")
    
    data = {}
    data['artist'] = input("Artist: ").strip()
    data['track'] = input("Track: ").strip()
    data['album'] = input("Album: ").strip()
    data['spotify_uri'] = input("Spotify URI (spotify:track:xxxx): ").strip()
    
    # Get duration in format HH:MM:SS and convert to milliseconds
    duration_input = input("Duration (HH:MM:SS): ").strip()
    h, m, s = map(int, duration_input.split(':'))
    data['duration_ms'] = str((h * 3600 + m * 60 + s) * 1000)
    
    data['spotify_url'] = input("Spotify URL: ").strip()
    data['youtube_url'] = input("YouTube URL: ").strip()
    data['likes'] = input("Likes: ").strip()
    data['views'] = input("Views: ").strip()
    
    if validate_song_data(data):
        try:
            with open("music.csv", 'a', newline='', encoding='utf-8') as file:
                fieldnames = ['Artist', 'Track', 'Album', 'Uri_spotify', 'Duration_ms', 
                              'Url_spotify', 'Url_youtube', 'Stream', 'Likes', 'Views']
                
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Check if file is empty and write header if needed
                if os.path.getsize("music.csv") == 0:
                    writer.writeheader()
                
                writer.writerow({
                    'Artist': data['artist'],
                    'Track': data['track'],
                    'Album': data['album'],
                    'Uri_spotify': data['spotify_uri'],
                    'Duration_ms': data['duration_ms'],
                    'Url_spotify': data['spotify_url'],
                    'Url_youtube': data['youtube_url'],
                    'Stream': '0',  # Default values for new songs
                    'Likes': data['likes'],
                    'Views': data['views']
                })
                
            print("Song added successfully!")
        except Exception as e:
            print(f"Error writing to file: {e}")
    else:
        print("Song data invalid. Please try again.")

def insert_song_batch() -> None:
    """Insert songs from a CSV file"""
    file_path = input("\nEnter CSV file path: ").strip()
    
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return
        
    try:
        valid_records = 0
        invalid_records = 0
        
        with open(file_path, 'r', encoding='utf-8') as input_file:
            csv_reader = csv.DictReader(input_file)
            
            with open("music.csv", 'a', newline='', encoding='utf-8') as output_file:
                fieldnames = ['Artist', 'Track', 'Album', 'Uri_spotify', 'Duration_ms', 
                              'Url_spotify', 'Url_youtube', 'Stream', 'Likes', 'Views']
                
                writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                
                # Check if file is empty and write header if needed
                if os.path.getsize("music.csv") == 0:
                    writer.writeheader()
                
                for row in csv_reader:
                    try:
                        data = {
                            'artist': row.get('Artist', ''),
                            'track': row.get('Track', ''),
                            'album': row.get('Album', ''),
                            'spotify_uri': row.get('Uri_spotify', ''),
                            'duration_ms': row.get('Duration_ms', '0'),
                            'spotify_url': row.get('Url_spotify', ''),
                            'youtube_url': row.get('Url_youtube', ''),
                            'likes': row.get('Likes', '0'),
                            'views': row.get('Views', '0')
                        }
                        
                        if validate_song_data(data):
                            writer.writerow({
                                'Artist': data['artist'],
                                'Track': data['track'],
                                'Album': data['album'],
                                'Uri_spotify': data['spotify_uri'],
                                'Duration_ms': data['duration_ms'],
                                'Url_spotify': data['spotify_url'],
                                'Url_youtube': data['youtube_url'],
                                'Stream': row.get('Stream', '0'),
                                'Likes': data['likes'],
                                'Views': data['views']
                            })
                            valid_records += 1
                        else:
                            invalid_records += 1
                    except Exception as e:
                        print(f"Error processing row: {e}")
                        invalid_records += 1
                        
        print(f"Import complete: {valid_records} records imported, {invalid_records} records skipped.")
    except Exception as e:
        print(f"Error reading from file: {e}")

def insert_song() -> None:
    """Insert song menu"""
    while True:
        print("\nInsert Song Menu:")
        print("1. Insert manually")
        print("2. Import from CSV file")
        print("3. Return to main menu")
        
        option = input("\nSelect an option: ").strip()
        
        if option == "1":
            insert_song_manual()
        elif option == "2":
            insert_song_batch()
        elif option == "3":
            break
        else:
            print("Invalid option")

def show_albums() -> None:
    """Show albums for a specific artist"""
    songs = parse_csv()
    
    artist_name = input("\nEnter artist name: ").strip()
    
    # Filter songs by artist (case insensitive)
    pattern = re.compile(artist_name, re.IGNORECASE)
    artist_songs = [song for song in songs if pattern.search(song.artist)]
    
    if not artist_songs:
        print(f"No songs found for artist '{artist_name}'.")
        return
    
    # Group songs by album
    albums = {}
    for song in artist_songs:
        if song.album not in albums:
            albums[song.album] = {
                'songs': [],
                'total_duration': 0
            }
        albums[song.album]['songs'].append(song)
        albums[song.album]['total_duration'] += song.duration_ms
    
    print(f"\nFound {len(albums)} albums for {artist_name}:")
    
    for album_name, album_data in albums.items():
        song_count = len(album_data['songs'])
        total_duration = convert_duration(album_data['total_duration'])
        
        print(f"Album: {album_name}")
        print(f"Songs: {song_count}")
        print(f"Total Duration: {total_duration}")
        print("-" * 50)

def main():
    while True:
        print("\nMenu:")
        print("1. Search by title or artist")
        print("2. Top songs by artist")
        print("3. Insert a record")
        print("4. Show albums by artist")
        print("5. Exit")
        
        option = input("\nSelect an option: ").strip()
        
        if option == "1":
            search_songs()
        elif option == "2":
            artist_top_songs()
        elif option == "3":
            insert_song()
        elif option == "4":
            show_albums()
        elif option == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()
