from src.lexer import tokenize
from src.parse import *

exmeplo = '''
const a = 5;
'''

res = WabbitParser().parse( tokenize(exmeplo) )
print(res)