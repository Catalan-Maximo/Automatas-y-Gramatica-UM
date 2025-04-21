class AFN:
    def __init__(self, estados: set, alfabeto: set, transiciones: dict, estado_inicial: str, estados_aceptacion: set):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = estados_aceptacion

    def epsilon_cerradura(self, estados):
        cerradura = set(estados)
        pila = list(estados)
        while pila:
            estado = pila.pop()
            if estado in self.transiciones and 'e' in self.transiciones[estado]:
                for siguiente_estado in self.transiciones[estado]['e']:
                    if siguiente_estado not in cerradura:
                        cerradura.add(siguiente_estado)
                        pila.append(siguiente_estado)
        return cerradura

    def transitar(self, estados, simbolo):
        siguiente_estados = set()
        for estado in estados:
            if estado in self.transiciones and simbolo in self.transiciones[estado]:
                siguiente_estados.update(self.transiciones[estado][simbolo])
        return siguiente_estados

    def acepta(self, cadena):
        estado_actual = self.epsilon_cerradura({self.estado_inicial})
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False
            estado_actual = self.transitar(estado_actual, simbolo)
            estado_actual = self.epsilon_cerradura(estado_actual)
        return any(estado in self.estados_aceptacion for estado in estado_actual)


# Definir los elementos del AFN
estados = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'}
alfabeto = {'a', 'b'}
transiciones = {
    '0': {'e': {'1', '7'}},
    '1': {'e': {'2', '4'}},
    '2': {'a': {'3'}},
    '3': {'e': {'6'}},
    '4': {'b': {'5'}},
    '5': {'e': {'6'}},
    '6': {'e': {'1', '7'}},
    '7': {'a': {'8'}, 'b': {'9'}, 'e': {'10'}},
}
estado_inicial = '0'
estados_aceptacion = {'8', '9', '10'}

# Crear el autómata
prueba = AFN(estados, alfabeto, transiciones, estado_inicial, estados_aceptacion)

# Probar con cadenas
cadenas = [
    'abbba',
    'b',
    'a',
    'abb',
    '',
    'c',
]

for cadena in cadenas:
    if prueba.acepta(cadena):
        print(f'La cadena "{cadena}" es aceptada')
    else:
        print(f'La cadena "{cadena}" NO es aceptada')

