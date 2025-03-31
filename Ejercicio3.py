import re
from collections import Counter

#Ejercicio hecho por: Alexander Ovalle, Maximo Catalan 

def validar_email(email):
    patron = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.-]*@[a-zA-Z]+\.(com|net|org|edu|gov)\.(arg|cl|es|mx|eeuu)$')
    return bool(patron.match(email))

def validar_url(url):
    patron = re.compile(r'^(https?:\/\/)?(www\.)?[a-zA-Z0-9.-]+\.(com|net|org|edu|gov)(\/|\?.*)?$')
    return bool(patron.match(url))

def validar_ipv4(ip):
    patron = re.compile(r'^(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.'
                        r'(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})\.(25[0-5]|2[0-4][0-9]|1?[0-9]{1,2})$')
    return bool(patron.match(ip))

def contar_palabras(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        texto = f.read().lower()
        palabras = re.findall(r'\b\w+\b', texto)
        contador = Counter(palabras)
        palabra_mas_comun = contador.most_common(1)
        return len(palabras), palabra_mas_comun[0] if palabra_mas_comun else (None, 0)

def analizar_archivo(archivo, funcion_validadora):
    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            cadena = linea.strip()
            resultado = "Válido" if funcion_validadora(cadena) else "Inválido"
            print(f"{cadena}: {resultado}")

def menu():
    while True:
        print("\n--- MENÚ ---")
        print("1. Validar Emails")
        print("2. Validar URLs")
        print("3. Validar IPv4")
        print("4. Contar palabras en un texto")
        print("5. Salir")
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            print("\nValidación de Emails:")
            analizar_archivo("emails.txt", validar_email)
        elif opcion == "2":
            print("\nValidación de URLs:")
            analizar_archivo("urls.txt", validar_url)
        elif opcion == "3":
            print("\nValidación de IPv4:")
            analizar_archivo("ips.txt", validar_ipv4)
        elif opcion == "4":
            print("\nConteo de palabras:")
            num_palabras, palabra_mas_repetida = contar_palabras("texto.txt")
            print(f"Total de palabras: {num_palabras}")
            print(f"Palabra más repetida: '{palabra_mas_repetida[0]}' con {palabra_mas_repetida[1]} apariciones")
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    menu()
