import pathlib
import csv
from dataclasses import dataclass

# Creamos clase DTO que representa una fila.
# Ver https://realpython.com/python-data-classes
@dataclass
class MovieDto:
    title: str
    year: str
    age: str
    rating: float
    available_in_netflix: bool
    available_in_hulu: bool
    available_in_prime_video: bool
    available_in_disney_plus: bool

    def rating_as_float(self) -> float:
        score = int(self.rating.split('/')[0])
        return score / 100

def parse_csv() -> list:
    movies = []
    try:
        # Abrir el archivo csv usando path relativo desde este archivo Python
        with open(f"{pathlib.Path(__file__).parent.absolute()}/movies.csv", 'r', encoding='latin-1') as file:
            # Usamos csv.DictReader que permite leer el archivo y parsear cada fila a un diccionario Python.
            # ver https://realpython.com/python-csv/
            csv_reader = csv.DictReader(file, delimiter=',')
            for row in csv_reader:
                # Parseamos cada row a la clase DTO. Lo agregamos a la lista
                movie = MovieDto(
                    row['Title'],
                    row['Year'],
                    row['Age'],
                    row['Rating'],
                    row['Netflix'] == '1',
                    row['Hulu'] == '1',
                    row['Prime Video'] == '1',
                    row['Disney+'] == '1',
                )
                movies.append(movie)
        return movies
    except FileNotFoundError:
        print("File not found")
        exit(1)

def search_by_title(movies: list, search_text: str) -> list:
    """Busca películas cuyo título contenga el texto de búsqueda (case insensitive)"""
    search_text = search_text.lower()
    return [movie for movie in movies if search_text in movie.title.lower()]

def search_by_platform_and_age(movies: list, platform: str, age_category: str) -> list:
    """Busca películas por plataforma y categoría de edad, ordenadas por rating"""
    filtered_movies = []
    
    for movie in movies:
        # Verificar si la película está en la plataforma seleccionada
        is_in_platform = False
        if platform == "Netflix" and movie.available_in_netflix:
            is_in_platform = True
        elif platform == "Hulu" and movie.available_in_hulu:
            is_in_platform = True
        elif platform == "Prime Video" and movie.available_in_prime_video:
            is_in_platform = True
        elif platform == "Disney+" and movie.available_in_disney_plus:
            is_in_platform = True
        
        # Si está en la plataforma y coincide con la categoría de edad, incluirla
        if is_in_platform and movie.age == age_category:
            filtered_movies.append(movie)
    
    # Ordenar por rating de mayor a menor y tomar los primeros 10
    sorted_movies = sorted(filtered_movies, key=lambda m: m.rating_as_float(), reverse=True)
    return sorted_movies[:10]

def get_platform_selection() -> str:
    """Muestra las plataformas disponibles y devuelve la selección del usuario"""
    print("\nSeleccione una plataforma:")
    print("1 - Netflix")
    print("2 - Hulu")
    print("3 - Prime Video")
    print("4 - Disney+")
    
    platforms = {1: "Netflix", 2: "Hulu", 3: "Prime Video", 4: "Disney+"}
    
    while True:
        try:
            option = int(input("Ingrese el número de la plataforma: "))
            if 1 <= option <= 4:
                return platforms[option]
            else:
                print("Opción inválida. Ingrese un número del 1 al 4.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def get_age_categories(movies: list) -> list:
    """Obtiene todas las categorías de edad disponibles en las películas"""
    categories = set()
    for movie in movies:
        categories.add(movie.age)
    return sorted(list(categories))

def get_age_selection(movies: list) -> str:
    """Muestra las categorías de edad disponibles y devuelve la selección del usuario"""
    age_categories = get_age_categories(movies)
    
    print("\nSeleccione una categoría de edad:")
    for i, category in enumerate(age_categories, 1):
        print(f"{i} - {category}")
    
    while True:
        try:
            option = int(input("Ingrese el número de la categoría: "))
            if 1 <= option <= len(age_categories):
                return age_categories[option-1]
            else:
                print(f"Opción inválida. Ingrese un número del 1 al {len(age_categories)}.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def display_movies(movies: list):
    """Muestra información de una lista de películas"""
    if not movies:
        print("No se encontraron películas que coincidan con la búsqueda.")
        return
    
    print(f"\nSe encontraron {len(movies)} películas:")
    for i, movie in enumerate(movies, 1):
        platforms = []
        if movie.available_in_netflix:
            platforms.append("Netflix")
        if movie.available_in_hulu:
            platforms.append("Hulu")
        if movie.available_in_prime_video:
            platforms.append("Prime Video")
        if movie.available_in_disney_plus:
            platforms.append("Disney+")
        
        platforms_str = ", ".join(platforms) if platforms else "Ninguna"
        print(f"{i}. {movie.title} ({movie.year}) - Rating: {movie.rating} - Plataformas: {platforms_str}")

def show_menu():
    """Muestra el menú principal del programa"""
    print("\n--- MENÚ PELÍCULAS ---")
    print("1 - Buscar por título")
    print("2 - Buscar por plataforma y categoría de edad")
    print("3 - Agregar nueva película")  # Nueva opción
    print("0 - Salir")
    
    try:
        option = int(input("Seleccione una opción: "))
        return option
    except ValueError:
        print("Por favor, ingrese un número válido.")
        return -1

def get_yes_no_input(prompt):
    while True:
        response = input(prompt).strip().lower()
        if response == 's' or response == 'n':
            return response == 's'
        else:
            print("Error: Por favor, ingrese solo 's' o 'n'.")

def add_new_movie(movies: list):
    """Recopila y valida los datos para una nueva película"""
    print("\n--- AGREGAR NUEVA PELÍCULA ---")
    
    # Título
    while True:
        title = input("Título: ").strip()
        if not title:
            print("Error: El título no puede estar vacío.")
        else:
            break
    
    # Año
    current_year = 2025  # Podría usar datetime.now().year para obtener el año actual
    while True:
        try:
            year = input(f"Año (1900-{current_year}): ").strip()
            year_int = int(year)
            if 1900 <= year_int <= current_year:
                break
            else:
                print(f"Error: El año debe estar entre 1900 y {current_year}.")
        except ValueError:
            print("Error: El año debe ser un número entero válido.")
    
    # Categoría de edad
    age_categories = get_age_categories(movies)
    print("\nCategorías de edad disponibles:")
    for i, category in enumerate(age_categories, 1):
        print(f"{i} - {category}")
    
    while True:
        try:
            option = int(input("Seleccione una categoría de edad: "))
            if 1 <= option <= len(age_categories):
                age = age_categories[option-1]
                break
            else:
                print(f"Error: Opción inválida. Seleccione un número del 1 al {len(age_categories)}.")
        except ValueError:
            print("Error: Por favor, ingrese un número válido.")
    
    # Rating
    while True:
        try:
            rating_value = int(input("Rating (0-100): ").strip())
            if 0 <= rating_value <= 100:
                rating = f"{rating_value}/100"
                break
            else:
                print("Error: El rating debe estar entre 0 y 100.")
        except ValueError:
            print("Error: El rating debe ser un número entero válido.")
    
    # Disponibilidad en plataformas
    netflix = get_yes_no_input("¿Disponible en Netflix? (s/n): ")
    hulu = get_yes_no_input("¿Disponible en Hulu? (s/n): ")
    prime_video = get_yes_no_input("¿Disponible en Prime Video? (s/n): ")
    disney_plus = get_yes_no_input("¿Disponible en Disney+? (s/n): ")
    
    # Crear y agregar la nueva película
    new_movie = MovieDto(
        title,
        year,
        age,
        rating,
        netflix,
        hulu,
        prime_video,
        disney_plus
    )
    
    movies.append(new_movie)
    
    # Guardar en el archivo CSV
    if save_to_csv(movies):
        print(f"\n¡Película '{title}' agregada correctamente!")
    else:
        print("Error: No se pudo guardar la película en el archivo.")

def save_to_csv(movies: list) -> bool:
    """Guarda la lista de películas en el archivo CSV"""
    try:
        csv_path = f"{pathlib.Path(__file__).parent.absolute()}/movies.csv"
        with open(csv_path, 'w', newline='', encoding='latin-1') as file:
            fieldnames = ['Title', 'Year', 'Age', 'Rating', 'Netflix', 'Hulu', 'Prime Video', 'Disney+']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for movie in movies:
                writer.writerow({
                    'Title': movie.title,
                    'Year': movie.year,
                    'Age': movie.age,
                    'Rating': movie.rating,
                    'Netflix': '1' if movie.available_in_netflix else '0',
                    'Hulu': '1' if movie.available_in_hulu else '0',
                    'Prime Video': '1' if movie.available_in_prime_video else '0',
                    'Disney+': '1' if movie.available_in_disney_plus else '0',
                })
        return True
    except Exception as e:
        print(f"Error al guardar el archivo CSV: {e}")
        return False

if __name__ == '__main__':
    # Cargar las películas del CSV
    print("Cargando datos de películas...")
    movies = parse_csv()
    print(f"Se cargaron {len(movies)} películas correctamente.")
    
    # Mostrar menú y procesar opciones
    while True:
        option = show_menu()
        
        if option == 0:
            print("¡Hasta luego!")
            break
        elif option == 1:
            search_text = input("Ingrese el título a buscar: ")
            results = search_by_title(movies, search_text)
            display_movies(results)
        elif option == 2:
            platform = get_platform_selection()
            age_category = get_age_selection(movies)
            results = search_by_platform_and_age(movies, platform, age_category)
            print(f"\nMostrando las primeras 10 películas de categoría {age_category} en {platform} (ordenadas por rating):")
            display_movies(results)
        elif option == 3:
            add_new_movie(movies)  # Llamada a la nueva función
        else:
            print("Opción no válida, intente nuevamente.")