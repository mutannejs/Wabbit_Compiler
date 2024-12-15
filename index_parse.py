from src.lexer import tokenize
from src.parse import *

exmeplo = '''
false
'''

res = WabbitParser().parse( tokenize(exmeplo) )
print(res)