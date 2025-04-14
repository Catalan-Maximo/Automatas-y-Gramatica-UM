def solve(expr):
    suma_partes = expr.split('+')
    total = 0
    for parte in suma_partes:
        multiplicaciones = parte.split('*')
        producto = 1
        for num in multiplicaciones:
            producto *= int(num)
        total += producto
    return total

print(solve("2 + 7 * 2 + 1"))
print(solve("2 * 2 * 2 + 32 * 2"))
            