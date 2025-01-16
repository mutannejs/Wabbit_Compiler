from src.tokenize import tokenize
from src.parse import WabbitParser
from src.to_source import to_source
from src.typecheck import check_program
from src.interp import *
from src.c import compile_program

from examples.examples_parse import examples

# examples = [

# '''// Short-circuit evaluation
# // Note: Implementing this is likely to be tricky/messy.
# // Come back to it later if you have other things to fix.

# var x = 1;
# var y = 0;

# print true || (x/y == 0);
# print false && (x/y == 0);''',

# r"""var a int = 5.5;
# const b = 10;
# var i = { (b / 10) - 1; };
# while i < 10.0 {
#     print i;
#     if () {
#         print false;
#         continue;
#     }
#     i = i + 1;
# }
# break;
# """

# ]

for i in range( len(examples[:]) ):
    ex = examples[i]

    print(f'\n\n========= Exemplo {i} =========')
    tokens = tokenize(ex)

    # for tok in tokens:
    #     print(tok)
    # continue

    res = WabbitParser().parse( tokens )
    print( res, end='\n\n' )
    print( to_source(res) )
    ok, res_ch = check_program(res)
    if ok:
        interpret_program(res_ch)
        res_co = compile_program(res_ch)

        f = open(f"langc/test{i}.c", 'x+')
        f.writelines(res_co)
        f.close()