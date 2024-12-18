from src.tokenize import tokenize
from src.parse import *

exmeplo = '''
while 5 == 10 {
    print 5;
    var a unit = ();
}
'''

res = WabbitParser().parse( tokenize(exmeplo) )
print(res)