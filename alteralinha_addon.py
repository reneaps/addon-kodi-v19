import os
import sys

# Compatibility with 3.0, 3.1 and 3.2 not supporting u"" literals
if sys.version < '3':
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]
else:
    def u(x):
        return x

arquivo = open('addon.py', 'r')
x = 1
data = u""
for linha in arquivo:
    linha = linha.rstrip()
    if 'xbmc.log' in linha :
        n = linha.find('] L')
        b = u(linha[n:n+6])
        c = u('] L' + str(x))
        if len(c) == 5 : c = c + ' '
        linha = linha.replace(b,c)
    print(x,linha)
    data += u(linha + "\n")
    x += 1
    #x = x + 1
    #print(x)

file = "addon2.py"

try:
    # write data to the file (use b for Python 3)
    open(file, "w" ).write( data )
except Exception as e:
    # oops
    print("An error occurred saving %s file!\n%s" % ( file, e ))

arquivo.close()
