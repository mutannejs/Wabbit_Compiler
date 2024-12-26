from src.parse import WabbitParser
from src.interp import *
from src.tokenize import tokenize
from src.typecheck import check_program

# from examples.examples_typecheck import examples

examples = [
r"""var a int = 5.5;
const b = 10;
var i = { (b / 10) - 1; };
while i < 10.0 {
    print i;
    if () {
        print false;
        continue;
    }
    i = i + 1;
}
break;
"""
]

for i in range( len(examples[:]) ):
    ex = examples[i]

    print(f'\n\n========= Exemplo {i} =========')
    tokens = tokenize(ex)
    # for tok in tokens:
    #     print(tok)
    res = WabbitParser().parse( tokens )
    print( res, end='\n\n' )
    print( to_source(res) )
    ok = check_program(res)
    if ok:
        interpret_program(res)