import pathlib
import csv
from dataclasses import dataclass
from typing import List

# --- Clase que representa una película ---
@dataclass
class MovieDto:
    title: str
    year: str
    age: str
    rating: str
    netflix: bool
    hulu: bool
    prime_video: bool
    disney_plus: bool

    def rating_as_float(self) -> float:
        try:
            return float(self.rating.split('/')[0]) / 100  # Convierte "98/100" a 0.98
        except (ValueError, IndexError):
            return 0.0

# --- Leer archivo CSV ---
def parse_csv() -> List[MovieDto]:
    movies = []
    try:
        ruta = pathlib.Path(__file__).parent / "movies.csv"
        with open(ruta, 'r', encoding='utf-8') as archivo:
            csv_reader = csv.DictReader(archivo, delimiter=',')
            for row in csv_reader:
                movie = MovieDto(
                    row['Title'],
                    row['Release Year'],
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
        print("Archivo movies.csv no encontrado.")
        exit(1)

# --- Guardar archivo CSV ---
def save_csv(movies: List[MovieDto]):
    ruta = pathlib.Path(__file__).parent / "movies.csv"
    with open(ruta, 'w', encoding='utf-8', newline='') as archivo:
        fieldnames = ['Title', 'Release Year', 'Age', 'Rating', 'Netflix', 'Hulu', 'Prime Video', 'Disney+']
        writer = csv.DictWriter(archivo, fieldnames=fieldnames)
        writer.writeheader()
        for movie in movies:
            writer.writerow({
                'Title': movie.title,
                'Release Year': movie.year,
                'Age': movie.age,
                'Rating': movie.rating,
                'Netflix': '1' if movie.netflix else '0',
                'Hulu': '1' if movie.hulu else '0',
                'Prime Video': '1' if movie.prime_video else '0',
                'Disney+': '1' if movie.disney_plus else '0',
            })

# --- Mostrar película encontrada ---
def mostrar_pelicula(m: MovieDto):
    print(f"{m.title} ({m.year}) - Edad: {m.age} - Rating: {m.rating}")

# --- Opción 1: Buscar por título ---
def buscar_por_titulo(movies: List[MovieDto]):
    busqueda = input("Ingrese parte del título de la película: ").lower().strip()
    encontrados = [m for m in movies if busqueda in m.title.lower()]

    if encontrados:
        print(f"\nSe encontraron {len(encontrados)} resultado(s):\n")
        for m in encontrados:
            mostrar_pelicula(m)
    else:
        print("No se encontraron películas con ese título.")

# --- Opción 2: Buscar por plataforma y categoría ---
def buscar_por_plataforma_y_categoria(movies: List[MovieDto]):
    plataformas = {
        "Netflix": "netflix",
        "Hulu": "hulu",
        "Prime Video": "prime_video",
        "Disney+": "disney_plus"
    }
    plataforma = input("Ingrese la plataforma (Netflix, Hulu, Prime Video, Disney+): ").strip()
    categoria = input("Ingrese la categoría de edad (7+, 13+, 16+, 18+, all): ").strip()

    if plataforma not in plataformas:
        print("Plataforma no válida.")
        return

    encontrados = [
        m for m in movies
        if getattr(m, plataformas[plataforma]) and (m.age == categoria or categoria == "all")
    ]

    if encontrados:
        print(f"\nSe encontraron {len(encontrados)} resultado(s):\n")
        for m in encontrados:
            mostrar_pelicula(m)
    else:
        print("No se encontraron películas para esa plataforma y categoría.")

# --- Opción 3: Insertar una nueva película ---
def insertar_pelicula(movies: List[MovieDto]):
    title = input("Ingrese el título de la película: ").strip()
    year = input("Ingrese el año de lanzamiento: ").strip()
    age = input("Ingrese la categoría de edad (7+, 13+, 16+, 18+): ").strip()
    rating = input("Ingrese el rating (por ejemplo, 85/100): ").strip()
    netflix = input("¿Está disponible en Netflix? (s/n): ").strip().lower() == 's'
    hulu = input("¿Está disponible en Hulu? (s/n): ").strip().lower() == 's'
    prime_video = input("¿Está disponible en Prime Video? (s/n): ").strip().lower() == 's'
    disney_plus = input("¿Está disponible en Disney+? (s/n): ").strip().lower() == 's'

    nueva_pelicula = MovieDto(title, year, age, rating, netflix, hulu, prime_video, disney_plus)
    movies.append(nueva_pelicula)
    save_csv(movies)
    print("Película agregada exitosamente.")

# --- Menú principal ---
def menu():
    movies = parse_csv()
    while True:
        print("\nMenú:")
        print("1 - Buscar por título")
        print("2 - Buscar por plataforma y categoría")
        print("3 - Insertar una nueva película")
        print("4 - Salir")
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            buscar_por_titulo(movies)
        elif opcion == "2":
            buscar_por_plataforma_y_categoria(movies)
        elif opcion == "3":
            insertar_pelicula(movies)
        elif opcion == "4":
            print("Saliendo del programa...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

# --- Ejecutar el programa ---
if __name__ == "__main__":
    menu()