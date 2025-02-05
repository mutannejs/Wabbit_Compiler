from src.tokenize import tokenize
from src.parse import WabbitParser
from src.to_source import to_source
from src.typecheck import check_program
from src.interp import *
from src.c import compile_program
from src.transform import transform_program
from src.generate import generate_program, encode_module

from examples.examples_generate import examples

# examples = [ ]

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
        res_tm = transform_program(res_ch)
        print( res_tm )
        print( to_source(res_tm) )

        mod = generate_program(res_ch)
        wabbit_wasm = encode_module(mod.module)
        print(wabbit_wasm)
        with open('wasm/out.wasm', 'wb') as file:
            file.write(wabbit_wasm)

        print()
        interpret_program(res_tm)

        # res_co = compile_program(res_tm)
        # f = open(f"langc/test{i}.c", 'x+')
        # f.writelines(res_co)
        # f.close()