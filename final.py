import csv
import re
import os
import pathlib
from datetime import timedelta
from dataclasses import dataclass
from urllib.parse import urlparse

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
    """Convierte la duración de milisegundos al formato HH:MM:SS"""
    seconds = int(float(ms)) // 1000
    return str(timedelta(seconds=seconds))

def parse_csv() -> list:
    songs = []
    try:
        file_path = pathlib.Path(__file__).parent.absolute() / "music.csv"
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter=',')
            
            for row in csv_reader:
                try:
                    # Extraer valores con manejo seguro
                    stream_value = str(row.get('Stream', '0')).strip().split(';')[0]
                    views_value = str(row.get('Views', '0')).strip().split(';')[0]
                    stream_count = int(float(stream_value)) if stream_value else 0
                    views = int(float(views_value)) if views_value else 0
                    
                    song = SongDto(
                        artist=str(row.get('Artist', '')).strip(),
                        track=str(row.get('Track', '')).strip(),
                        album=str(row.get('Album', '')).strip(),
                        spotify_uri=str(row.get('Uri', '')).strip(),
                        duration_ms=int(float(row.get('Duration_ms', '0'))),
                        spotify_url=str(row.get('Url_spotify', '')).strip(),
                        youtube_url=str(row.get('Url_youtube', '')).strip(),
                        stream=stream_count,
                        likes=int(float(row.get('Likes', '0') or '0')),
                        views=views
                    )
                    songs.append(song)
                except (ValueError, KeyError, TypeError):
                    continue
                    
        return songs
    except FileNotFoundError:
        print("\nError: No se encontró el archivo music.csv")
        return []
    except Exception as e:
        print(f"\nError al leer el archivo: {e}")
        return []
    
def search_songs() -> None:
    songs = parse_csv()
    
    print("\nIngresa término de búsqueda para título o artista (presiona Enter sin texto para salir):")
    while True:
        search_term = input("> ").strip()
        
        if not search_term:
            break
            
        # Búsqueda usando comparación sin distinción de mayúsculas para mejor confiabilidad
        matches = [
            song for song in songs 
            if search_term.lower() in song.artist.lower() or search_term.lower() in song.track.lower()
        ]
        
        # Ordenar por conteo de vistas (descendente) si está disponible, de lo contrario por streams
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
    
    artist_name = input("\nIngresa nombre del artista: ").strip()

    artist_songs = [song for song in songs if artist_name.lower() in song.artist.lower()]
    
    # Ordenar por conteo de streams (descendente)
    artist_songs.sort(key=lambda x: (x.views if x.views > 0 else x.stream), reverse=True)
    
    # Obtener top 5 canciones
    top_songs = artist_songs[:5]
    
    if top_songs:
        print(f"\nTop 5 canciones de {artist_name}:")
        for i, song in enumerate(top_songs, 1):
            print(f"\nTop {i}:")
            print(f"Artista: {song.artist}")
            print(f"Duración: {convert_duration(song.duration_ms)}")
            if song.views > 0:
                views_m = song.views / 1_000_000
                print(f"Reproducciones: {views_m:.1f}M vistas")
            elif song.stream > 0:
                stream_m = song.stream / 1_000_000
                print(f"Reproducciones: {stream_m:.1f}M streams")
            print("-" * 50)
    else:
        print(f"No se encontraron canciones para el artista '{artist_name}'.")

def spotify_url_to_uri(url):
    try:
        # Parsear la URL
        parsed_url = urlparse(url)
       
        # Extraer el path y dividirlo
        path_parts = parsed_url.path.strip('/').split('/')
       
        # Buscar el tipo de contenido (track, album, playlist, etc.) y el ID
        content_type = None
        content_id = None
       
        for i, part in enumerate(path_parts):
            if part in ['track', 'album', 'playlist', 'artist', 'show', 'episode']:
                content_type = part
                # El ID debería estar en la siguiente posición
                if i + 1 < len(path_parts):
                    content_id = path_parts[i + 1]
                break
       
        if not content_type or not content_id:
            raise ValueError("No se pudo extraer el tipo de contenido o ID de la URL")
       
        # Crear la URI
        uri = f"spotify:{content_type}:{content_id}"
        return uri
       
    except Exception as e:
        raise ValueError(f"Error al procesar la URL: {str(e)}")

def validate_song_data(data: dict):
    # Patrones básicos de validación
    patterns = {
        'artist': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'track': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'album': r'^[A-Za-z0-9\s\.\,\-\_\'\&\(\)]+$',
        'spotify_uri': r'^spotify:(track|album|playlist|artist|show|episode):[a-zA-Z0-9]{22}$',
        'duration_ms': r'^\d+$',
        'spotify_url': r'^https://open\.spotify\.com/(intl-[a-z]{2}/)?((track|album|playlist|artist|show|episode)/[a-zA-Z0-9]{22})(\?.*)?$',
        'youtube_url': r'^https://(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_\-]{11}.*$',
        'likes': r'^\d+(\.\d+)?$',
        'views': r'^\d+(\.\d+)?$'
    }

    # Validar todos los campos
    for field, pattern in patterns.items():
        if field in data and data[field]:
            if not re.match(pattern, str(data[field])):
                print(f"Formato inválido para {field}: {data[field]}")
                return False
    
    # Validar que los likes no sean más que las views
    if 'likes' in data and 'views' in data and data['likes'] and data['views']:
        try:
            likes_val = float(data['likes'])
            views_val = float(data['views'])
            if likes_val > views_val:
                print("Error: Los likes no pueden ser más que las vistas.")
                return False
        except ValueError:
            print("Error: Los likes y vistas deben ser valores numéricos.")
            return False
            
    return True

def get_next_index():
    """Obtiene el siguiente índice disponible del archivo CSV"""
    try:
        if not os.path.exists("music.csv") or os.path.getsize("music.csv") == 0:
            return 0
        
        with open("music.csv", 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            last_index = -1
            
            for row in csv_reader:
                index_value = row.get('Index', '').strip()
                if index_value and index_value.isdigit():
                    last_index = max(last_index, int(index_value))
            
            return last_index + 1
    except Exception:
        return 0

def insert_song_manual() -> None:
    """Insertar una canción manualmente desde entrada de terminal"""
    print("\nInsertar datos de nueva canción:")
    
    data = {}
    data['artist'] = input("Artista: ").strip()
    data['track'] = input("Canción: ").strip()
    data['album'] = input("Álbum: ").strip()
    
    # Obtener URL de Spotify y convertir automáticamente a URI
    spotify_url = input("URL de Spotify: ").strip()
    data['spotify_url'] = spotify_url
    
    # Convertir automáticamente URL de Spotify a URI si se proporciona
    if spotify_url:
        try:
            spotify_uri = spotify_url_to_uri(spotify_url)
            data['spotify_uri'] = spotify_uri
            print(f"URI de Spotify generado automáticamente: {spotify_uri}")
        except ValueError as e:
            print(f"Error convirtiendo URL de Spotify: {e}")
            # Pedir entrada manual de URI si la conversión falla
            data['spotify_uri'] = input("Por favor ingresa URI de Spotify manualmente (spotify:track:xxxx): ").strip()
    else:
        # Si no se proporciona URL, pedir URI
        data['spotify_uri'] = input("URI de Spotify (spotify:track:xxxx): ").strip()
    
    # Obtener duración en formato HH:MM:SS y convertir a milisegundos
    duration_input = input("Duración (HH:MM:SS): ").strip()
    h, m, s = map(int, duration_input.split(':'))
    data['duration_ms'] = str((h * 3600 + m * 60 + s) * 1000)
    
    data['youtube_url'] = input("URL de YouTube: ").strip()
    data['likes'] = input("Likes: ").strip()
    data['views'] = input("Vistas: ").strip()
    
    if validate_song_data(data):
        try:
            # Obtener el siguiente índice disponible
            next_index = get_next_index()

            with open("music.csv", 'a', newline='', encoding='utf-8') as file:
                fieldnames = ['Index','Artist','Url_spotify','Track','Album','Album_type','Uri',
                              'Danceability','Energy','Key','Loudness','Speechiness','Acousticness',
                              'Instrumentalness','Liveness','Valence','Tempo','Duration_ms','Url_youtube',
                              'Title','Channel','Views','Likes','Comments','Licensed','official_video','Stream']
                
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                
                # Verificar si el archivo está vacío y escribir encabezado si es necesario
                if os.path.getsize("music.csv") == 0:
                    writer.writeheader()
                
                writer.writerow({
                    'Index': str(next_index),
                    'Artist': data['artist'],
                    'Url_spotify': data['spotify_url'],
                    'Track': data['track'],
                    'Album': data['album'],
                    'Album_type': '',  # Nulo
                    'Uri': data['spotify_uri'],
                    'Danceability': '',  # Nulo
                    'Energy': '',  # Nulo
                    'Key': '',  # Nulo
                    'Loudness': '',  # Nulo
                    'Speechiness': '',  # Nulo
                    'Acousticness': '',  # Nulo
                    'Instrumentalness': '',  # Nulo
                    'Liveness': '',  # Nulo
                    'Valence': '',  # Nulo
                    'Tempo': '',  # Nulo
                    'Duration_ms': data['duration_ms'],
                    'Url_youtube': data['youtube_url'],
                    'Title': '',  # Nulo
                    'Channel': '',  # Nulo
                    'Views': data['views'],
                    'Likes': data['likes'],
                    'Comments': '',  # Nulo
                    'Licensed': '',  # Nulo
                    'official_video': '',  # Nulo
                    'Stream': '0'  # Valores por defecto para nuevas canciones
                })
                
            print(f"¡Canción agregada exitosamente con Índice: {next_index}!")
        except Exception as e:
            print(f"Error escribiendo al archivo: {e}")
    else:
        print("Datos de canción inválidos. Por favor intenta de nuevo.")

def insert_song_batch() -> None:
    """Insertar canciones desde un archivo CSV"""
    file_path = input("\nIngresa ruta del archivo CSV: ").strip()
    
    if not os.path.exists(file_path):
        print(f"Archivo {file_path} no encontrado.")
        return
        
    try:
        valid_records = 0
        invalid_records = 0

        # Obtener índice inicial
        current_index = get_next_index()
        
        with open(file_path, 'r', encoding='utf-8') as input_file:
            csv_reader = csv.DictReader(input_file)
            
            with open("music.csv", 'a', newline='', encoding='utf-8') as output_file:
                fieldnames = ['Index','Artist','Url_spotify','Track','Album','Album_type','Uri',
                            'Danceability','Energy','Key','Loudness','Speechiness','Acousticness',
                            'Instrumentalness','Liveness','Valence','Tempo','Duration_ms','Url_youtube',
                            'Title','Channel','Views','Likes','Comments','Licensed','official_video','Stream']
                
                writer = csv.DictWriter(output_file, fieldnames=fieldnames)
                
                # Verificar si el archivo está vacío y escribir encabezado si es necesario
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
                                'Index': str(current_index),
                                'Artist': data['artist'],
                                'Url_spotify': data['spotify_url'],
                                'Track': data['track'],
                                'Album': data['album'],
                                'Album_type': '',  # Nulo
                                'Uri': data['spotify_uri'],
                                'Danceability': '',  # Nulo
                                'Energy': '',  # Nulo
                                'Key': '',  # Nulo
                                'Loudness': '',  # Nulo
                                'Speechiness': '',  # Nulo
                                'Acousticness': '',  # Nulo
                                'Instrumentalness': '',  # Nulo
                                'Liveness': '',  # Nulo
                                'Valence': '',  # Nulo
                                'Tempo': '',  # Nulo
                                'Duration_ms': data['duration_ms'],
                                'Url_youtube': data['youtube_url'],
                                'Title': '',  # Nulo
                                'Channel': '',  # Nulo
                                'Views': data['views'],
                                'Likes': data['likes'],
                                'Comments': '',  # Nulo
                                'Licensed': '',  # Nulo
                                'official_video': '',  # Nulo
                                'Stream': row.get('Stream', '0')
                            })
                            current_index += 1  # Incrementar para el siguiente registro
                            valid_records += 1
                        else:
                            invalid_records += 1
                    except Exception as e:
                        print(f"Error procesando fila: {e}")
                        invalid_records += 1
                        
        print(f"Importación completa: {valid_records} registros importados, {invalid_records} registros omitidos.")
    except Exception as e:
        print(f"Error leyendo del archivo: {e}")

def insert_song() -> None:
    """Menú de insertar canción"""
    while True:
        print("\nMenú Insertar Canción:")
        print("1. Insertar manualmente")
        print("2. Importar desde archivo CSV")
        print("3. Regresar al menú principal")
        
        option = input("\nSelecciona una opción: ").strip()
        
        if option == "1":
            insert_song_manual()
        elif option == "2":
            insert_song_batch()
        elif option == "3":
            break
        else:
            print("Opción inválida")

def show_albums() -> None:
    """Mostrar álbumes para un artista específico"""
    songs = parse_csv()
    
    artist_name = input("\nIngresa nombre del artista: ").strip()
    
    # Filtrar canciones por artista (sin distinción de mayúsculas)
    pattern = re.compile(artist_name, re.IGNORECASE)
    artist_songs = [song for song in songs if pattern.search(song.artist)]
    
    if not artist_songs:
        print(f"No se encontraron canciones para el artista '{artist_name}'.")
        return
    
    # Agrupar canciones por álbum
    albums = {}
    for song in artist_songs:
        if song.album not in albums:
            albums[song.album] = {
                'songs': [],
                'total_duration': 0
            }
        albums[song.album]['songs'].append(song)
        albums[song.album]['total_duration'] += song.duration_ms
    
    print(f"\nSe encontraron {len(albums)} álbumes para {artist_name}:")
    
    for album_name, album_data in albums.items():
        song_count = len(album_data['songs'])
        total_duration = convert_duration(album_data['total_duration'])
        
        print(f"Álbum: {album_name}")
        print(f"Canciones: {song_count}")
        print(f"Duración Total: {total_duration}")
        print("-" * 50)

def main():
    """Menú principal integrado"""
    while True:
        print("\n" + "="*50)
        print("           GESTOR DE BASE DE DATOS MUSICAL")
        print("="*50)
        print("1. Buscar por título o artista")
        print("2. Top canciones por artista")
        print("3. Insertar una canción")
        print("4. Mostrar álbumes por artista")
        print("5. Salir")
        print("="*50)
        
        option = input("\nSelecciona una opción (1-5): ").strip()
        
        if option == "1":
            search_songs()
        elif option == "2":
            artist_top_songs()
        elif option == "3":
            insert_song()
        elif option == "4":
            show_albums()
        elif option == "5":
            print("\n¡Thanks for using Music Database Manager! Goodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")

if __name__ == "__main__":
    main()