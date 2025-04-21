class AFD:
    def __init__(self, estados: set, alfabeto: set, transiciones: dict, estado_inicial: str, estados_aceptacion: set):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_aceptacion = estados_aceptacion

    def acepta(self, cadena):
        estado_actual = self.estado_inicial
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False
            if simbolo not in self.transiciones[estado_actual]:
                return False
            estado_actual = self.transiciones[estado_actual][simbolo]
        return estado_actual in self.estados_aceptacion
    
alfabeto = {'a', 'b'}
estados = {'A', 'B','C'}
estado_inicial = 'A'
transiciones = {
    'A': {'a': 'B', 'b': 'C'},
    'B': {'a': 'B', 'b': 'C'},
    'C': {'a': 'B', 'b': 'C'}
}
estados_aceptacion = {'A', 'B', 'C'}

prueba = AFD(estados, alfabeto, transiciones, estado_inicial, estados_aceptacion)

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