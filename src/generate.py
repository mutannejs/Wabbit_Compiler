from functools import singledispatch

import struct

from .model import *


class WasmType:
    i32 = b'\x7f'   # (32-bit int)
    i64 = b'\x7e'   # (64-bit int)
    f32 = b'\x7d'   # (32-bit float)
    f64 = b'\x7c'   # (64-bit float)

class WabbitWasmModule:
    def __init__(self, name: str):
        self.module = self
        self.name = name
        self.imported_functions: list[WasmImportedFunction] = [ ]
        self.functions: list[WasmFunction] = [ ]
        self.global_variables: list[WasmGlobalVariable] = [ ]
        self.countLabels = 0
        self.env = {}

    def encode(self):
        return Encode.module(self)

class WasmImportedFunction:
    '''
    A function defined outside of the Wasm environment
    '''
    def __init__(self, module: WabbitWasmModule, envname: str, name: str, argtypes: list[WasmType], rettypes: list[WasmType]):
        self.module = module
        self.envname = envname
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions)
        module.imported_functions.append(self)

class WasmFunction:
    '''
    A natively defined Wasm function
    '''
    def __init__(self, module: WabbitWasmModule, name: str, argtypes: list[WasmType], rettypes: list[WasmType]):
        self.module = module
        self.name = name
        self.argtypes = argtypes
        self.rettypes = rettypes
        self.idx = len(module.imported_functions) + len(module.functions)
        module.functions.append(self)

        # Code generation
        self.code = b''

        # Types of local variables
        self.local_types = []

    def iconst(self, value: int): # 32 bits
        self.code += b'\x41' + Encode.signed(value)

    def fconst(self, value: float): # 64 bits
        self.code += b'\x44' + Encode.f64(value)

    def iadd(self):
        self.code += b'\x6a'

    def isub(self):
        self.code += b'\x6b'

    def imul(self):
        self.code += b'\x6c'

    def idiv(self):
        self.code += b'\x6d'

    def ieqz(self):
        self.code += b'\x45'

    def ieq(self):
        self.code += b'\x46'

    def ineq(self):
        self.code += b'\x47'

    def ilt(self):
        self.code += b'\x48'

    def igt(self):
        self.code += b'\x4a'

    def ile(self):
        self.code += b'\x4c'

    def ige(self):
        self.code += b'\x4e'

    def iand(self):
        self.code += b'\x71'

    def ior(self):
        self.code += b'\x72'

    def fadd(self):
        self.code += b'\xa0'

    def fsub(self):
        self.code += b'\xa1'

    def fmul(self):
        self.code += b'\xa2'

    def fdiv(self):
        self.code += b'\xa3'

    def feq(self):
        self.code += b'\x61'

    def fneq(self):
        self.code += b'\x62'

    def flt(self):
        self.code += b'\x63'

    def fgt(self):
        self.code += b'\x64'

    def fle(self):
        self.code += b'\x65'

    def fge(self):
        self.code += b'\x66'

    def ref_null(self):
        self.code += b'\xd0'

    def ret(self):
        self.code += b'\x0f'

    def call(self, func):
        self.code += b'\x10' + Encode.unsigned(func.idx)

    def alloca(self, type: WasmType):
        idx = len(self.argtypes) + len(self.local_types)
        self.local_types.append(type)
        return idx

    def local_get(self, idx):
        self.code += b'\x20' + Encode.unsigned(idx)

    def local_set(self, idx):
        self.code += b'\x21' + Encode.unsigned(idx)

    def global_get(self, gvar):
        self.code += b'\x23' + Encode.unsigned(gvar.idx)

    def global_set(self, gvar):
        self.code += b'\x24' + Encode.unsigned(gvar.idx)

    def block(self):
        self.code += b'\x02\x40'

    def loop(self):
        self.code += b'\x03\x40'

    def if_start(self, dtype: WasmType = None):
        self.code += b'\x04'
        if dtype == None:
            self.code += b'\x40'
        else:
            self.code += dtype

    def else_block(self):
        self.code += b'\x05'

    def end(self):
        self.code += b'\x0b'

    def br(self, idx: int):
        self.code += b'\x0c' + Encode.signed(idx)

    def br_if(self, idx: int):
        self.code += b'\x0d' + Encode.signed(idx)

class WasmGlobalVariable:
    '''
    A natively defined Wasm global variable
    '''
    def __init__(self, module: WabbitWasmModule, name: str, type: WasmType, initializer):
        self.module = module
        self.name = name
        self.type = type
        self.initializer = initializer
        self.idx = len(module.global_variables)
        module.global_variables.append(self)

class Encode:
    def __init__(self):
        pass

    def unsigned(value: int):
        '''
        Produce an LEB128 encoded unsigned integer.
        '''
        parts = []
        while value:
            parts.append((value & 0x7f) | 0x80)
            value >>= 7
        if not parts:
            parts.append(0)
        parts[-1] &= 0x7f
        return bytes(parts)

    def signed(value: int):
        '''
        Produce a LEB128 encoded signed integer.
        '''
        parts = [ ]
        if value < 0:
            # Sign extend the value up to a multiple of 7 bits
            value = (1 << (value.bit_length() + (7 - value.bit_length() % 7))) + value
            negative = True
        else:
            negative = False
        while value:
            parts.append((value & 0x7f) | 0x80)
            value >>= 7
        if not parts or (not negative and parts[-1] & 0x40):
            parts.append(0)
        parts[-1] &= 0x7f
        return bytes(parts)

    def f64(value: float):
        '''
        Encode a 64-bit float point as little endian
        '''
        return struct.pack('<d', value)

    def vector(items):
        '''
        A size-prefixed collection of objects.  If items is already
        bytes, it is prepended by a length and returned.  If items
        is a list of byte-strings, the length of the list is prepended
        to byte-string formed by concatenating all of the items.
        '''
        if isinstance(items, bytes):
            return Encode.unsigned(len(items)) + items
        else:
            return Encode.unsigned(len(items)) + b''.join(items)

    def string(name):
        '''
        Encode a text name as a UTF-8 vector
        '''
        return Encode.vector(name.encode('utf-8'))

    def section(sectnum, contents):
        return bytes([sectnum]) + Encode.unsigned(len(contents)) + contents

    def signature(func):
        return b'\x60' + Encode.vector(func.argtypes) + Encode.vector(func.rettypes)

    def import_function(func):
        return (Encode.string(func.envname) +
                Encode.string(func.name) +
            b'\x00' +
            Encode.unsigned(func.idx))

    def export_function(func):
        return Encode.string(func.name) + b'\x00' + Encode.unsigned(func.idx)

    def function_code(func):
        localtypes = [ b'\x01' + ltype for ltype in func.local_types ]
        if not func.code[-1:] == b'\x0b':
            func.code += b'\x0b'
        code = Encode.vector(localtypes) + func.code
        return Encode.unsigned(len(code)) + code

    def vglobal(gvar):
        if gvar.type == WasmType.i32:
            return WasmType.i32 + b'\x01\x41' + Encode.signed(gvar.initializer) + b'\x0b'
        elif gvar.type == WasmType.f64:
            return WasmType.f64 + b'\x01\x44' + Encode.f64(gvar.initializer) + b'\x0b'

def encode_module(module):
    # section 1 - signatures
    all_funcs = module.imported_functions + module.functions
    signatures = [Encode.signature(func) for func in all_funcs]
    section1 = Encode.section(1, Encode.vector(signatures))

    # section 2 - Imports
    all_imports = [ Encode.import_function(func) for func in module.imported_functions ]
    section2 = Encode.section(2, Encode.vector(all_imports))

    # section 3 - Functions
    section3 = Encode.section(3, Encode.vector([Encode.unsigned(f.idx) for f in module.functions]))

    # section 6 - Globals
    all_globals = [ Encode.vglobal(gvar) for gvar in module.global_variables ]
    section6 = Encode.section(6, Encode.vector(all_globals))

    # section 7 - Exports
    all_exports = [ Encode.export_function(func) for func in module.functions ]
    section7 = Encode.section(7, Encode.vector(all_exports))

    # section 10 - Code
    all_code = [ Encode.function_code(func) for func in module.functions ]
    section10 = Encode.section(10, Encode.vector(all_code))

    return b''.join([b'\x00asm\x01\x00\x00\x00',
                    section1,
                    section2,
                    section3,
                    section6,
                    section7,
                    section10])

# Top-level function for generating code from the model
def generate_program(model):
    mod = WabbitWasmModule('wabbit')
    WasmImportedFunction(
        mod,
        'runtime',
        '_printi',
        [ WasmType.i32 ],
        [ ]
    )
    WasmImportedFunction(
        mod,
        'runtime',
        '_printf',
        [ WasmType.f64 ],
        [ ]
    )
    WasmImportedFunction(
        mod,
        'runtime',
        '_printb',
        [ WasmType.i32 ],
        [ ]
    )
    WasmImportedFunction(
        mod,
        'runtime',
        '_printc',
        [ WasmType.i32 ],
        [ ]
    )
    WasmImportedFunction(
        mod,
        'runtime',
        '_printu',
        [ ],
        [ ]
    )
    main = WasmFunction(
        mod,
        'main',
        [ ],
        [ WasmType.i32 ]
    )
    _generate(model, mod)
    main.iconst(0)
    main.ret()
    return mod


# Internal function to generate code for each node type
@singledispatch
def _generate(node: Node, mod: WabbitWasmModule):
    raise RuntimeError(f"Can't generate code for {node}")

rule = _generate.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _generate_literal(node: LiteralT, mod: WabbitWasmModule):
    if node.p_type == 'int':
        mod.functions[-1].iconst(node.value)
    if node.p_type == 'float':
        mod.functions[-1].fconst(node.value)
    if node.p_type == 'bool':
        mod.functions[-1].iconst(1 if node.value else 0)
    if node.p_type == 'char':
        mod.functions[-1].iconst(ord(node.value) if node.value != '\\n' else 10)
    if node.p_type == 'unit':
        mod.functions[-1].iconst(0)

@rule(BinOp)
def _generate_binop(node: BinOp, mod: WabbitWasmModule):
    lineno = node.lineno

    if not node.op in ['&&', '||']:
        _generate(node.left, mod)
        _generate(node.right, mod)

    false = Bool(lineno, False)
    false.p_type = 'bool'

    true = Bool(lineno, True)
    true.p_type = 'bool'

    truecmp = BinOp(lineno, '==', node.left, true)
    truecmp.p_type = 'bool'

    block_exec_right = BlockStatement( lineno, [ node.right ] )
    block_exec_right.p_type = 'bool'

    block_true = BlockStatement( lineno, [ true ] )
    block_true.p_type = 'bool'

    block_false = BlockStatement( lineno, [ false ] )
    block_false.p_type = 'bool'

    match node.op:
        case '+':
            if node.left.p_type == 'int': mod.functions[-1].iadd()
            else: mod.functions[-1].fadd()
        case '-':
            if node.left.p_type == 'int': mod.functions[-1].isub()
            else: mod.functions[-1].fsub()
        case '/':
            if node.left.p_type == 'int': mod.functions[-1].idiv()
            else: mod.functions[-1].fdiv()
        case '*':
            if node.left.p_type == 'int': mod.functions[-1].imul()
            else: mod.functions[-1].fmul()
        case '<':
            if node.left.p_type == 'float': mod.functions[-1].flt()
            else: mod.functions[-1].ilt()
        case '>':
            if node.left.p_type == 'float': mod.functions[-1].fgt()
            else: mod.functions[-1].igt()
        case '<=':
            if node.left.p_type == 'float': mod.functions[-1].fle()
            else: mod.functions[-1].ile()
        case '>=':
            if node.left.p_type == 'float': mod.functions[-1].fge()
            else: mod.functions[-1].ige()
        case '==':
            if node.left.p_type == 'float': mod.functions[-1].feq()
            else: mod.functions[-1].ieq()
        case '!=':
            if node.left.p_type == 'float': mod.functions[-1].fneq()
            else: mod.functions[-1].ineq()
        case '&&':
            _generate_ifstatement(
                IfStatement(
                    lineno,
                    node.left,
                    block_exec_right,
                    block_false,
                ), mod
            )
        case '||':
            _generate_ifstatement(
                IfStatement(
                    lineno,
                    truecmp if isinstance(node.left, Bool) else node.left,
                    block_true,
                    block_exec_right,
                ), mod
            )

@rule(UnOp)
def _generate_unop(node: UnOp, mod: WabbitWasmModule):
    _generate(node.expr, mod)

    if node.op == '!':
        mod.functions[-1].ieqz()
    elif node.op == '-' and node.p_type == 'int':
        mod.functions[-1].iconst(-1)
        mod.functions[-1].imul()
    elif node.op == '-' and node.p_type == 'float':
        mod.functions[-1].fconst(-1)
        mod.functions[-1].fmul()

@rule(PrintStatement)
def _generate_print_statement(node: PrintStatement, mod: WabbitWasmModule):
    _generate(node.expr, mod)
    for f in mod.imported_functions:
        if  node.expr.p_type == 'int' and f.name == '_printi' or \
            node.expr.p_type == 'float' and f.name == '_printf' or \
            node.expr.p_type == 'bool' and f.name == '_printb' or \
            node.expr.p_type == 'char' and f.name == '_printc' or \
            node.expr.p_type == 'unit' and f.name == '_printu':
            mod.functions[-1].call(f)
        else:
            continue
        break

@rule(Location)
def _generate_location(node: Location, mod: WabbitWasmModule):
    idx = mod.env.get(node.name)
    mod.functions[-1].local_get(idx)

@rule(VarDefinition)
@rule(ConstDefinition)
def _generate_definition(node: VarDefinition | ConstDefinition, mod: WabbitWasmModule):
    name = node.location.name

    if node.value != None:
        _generate(node.value, mod)

    if node.dtype == 'float' or node.value and node.value.p_type == 'float':
        idx = mod.functions[-1].alloca(WasmType.f64)
        if node.value == None: mod.functions[-1].fconst(0)
    else:
        idx = mod.functions[-1].alloca(WasmType.i32)
        if node.value == None: mod.functions[-1].iconst(0)

    mod.functions[-1].local_set(idx)

    mod.env[name] = idx

@rule(AssignmentStatement)
def _generate_assignmentstatement(node: AssignmentStatement, mod: WabbitWasmModule):
    idx = mod.env.get(node.location.name)

    _generate(node.value, mod)

    mod.functions[-1].local_set(idx)

@rule(IfStatement)
def _generate_ifstatement(node: IfStatement, mod: WabbitWasmModule):
    _generate(node.cmp, mod)
    mod.functions[-1].if_start(
        WasmType.f64 if node.block_if.p_type == 'float' else WasmType.i32
    )

    mod.countLabels += 1
    _generate_blockstatement(node.block_if, mod)

    if (node.block_else):
        mod.functions[-1].else_block()
        _generate_blockstatement(node.block_else, mod)

    mod.functions[-1].end()
    mod.countLabels -= 1

@rule(WhileStatement)
def _generate_whilestatement(node: WhileStatement, mod: WabbitWasmModule):

    mod.countLabels += 1
    mod.functions[-1].block()
    mod.functions[-1].loop()

    _generate(node.cmp, mod)
    mod.functions[-1].ieqz()
    mod.functions[-1].br_if(1)

    _generate(node.body, mod)
    mod.functions[-1].br(0)

    mod.functions[-1].end()
    mod.functions[-1].end()
    mod.countLabels -= 1

@rule(Break)
def _interpret_break(node: Break, mod: WabbitWasmModule):
    mod.functions[-1].br(mod.countLabels)

@rule(Continue)
def _interpret_continue(node: Continue, mod: WabbitWasmModule):
    mod.functions[-1].br(mod.countLabels - 1)

@rule(CompoundExpression)
def _generate_compoundexpression(node: BlockStatement, mod: WabbitWasmModule):
    # env.newScope()
    for inst in node.instructions[:-1]:
        if isinstance(inst, Statement):
            _generate(inst, mod)
    _generate(node.instructions[-1], mod)
    # env.popScope()

@rule(BlockStatement)
def _generate_blockstatement(node: BlockStatement, mod: WabbitWasmModule):
    # env.newScope()

    for inst in node.instructions:
        _generate(inst, mod)

    # env.popScope()