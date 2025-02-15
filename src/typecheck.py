from functools import singledispatch

from .model import *


ScopeType = Literal["global", "function", "while", "if", "else", "compoundexpression"]


class EnvRegister:
    def __init__(self, mut: bool, dtype: DType | tuple):
        self._mut = mut
        self._dtype = dtype

    def setDtype(self, value: DType | tuple):
        self._dtype = value


class Env:
    def __init__(self):
        self.stack = [{}]
        self.scopes: list[ScopeType] = [ "global" ]
        self.functions = {}
        self.returnType = None
        self.returnLineno = None
        self.expectRetType = None

    def newScope(self):
        self.stack.insert(0, {})

    def popScope(self, popScope: bool = True):
        self.stack.pop(0)
        if popScope: self.scopes.pop()

    def createRegister(self, name: str, mut: bool, dtype: DType | tuple):
        self.stack[0][name] = EnvRegister(mut, dtype)

    def setRegister(self, name: str, dtype: DType | tuple):
        for i in range( len(self.stack) ):
            reg: EnvRegister = self.stack[i].get(name)
            if reg:
                reg.setDtype(dtype)
                self.stack[i][name] = reg
                break

    def isMutable(self, name) -> bool:
        for i in range( len(self.stack) ):
            reg: EnvRegister = self.stack[i].get(name)
            if reg:
                return reg._mut

    def getRegister(self, name: str, deep: int = -1) -> DType | tuple | None:
        length = deep if deep < len(self.stack) and deep > -1 else len(self.stack)
        for i in range( length ):
            reg: EnvRegister = self.stack[i].get(name)
            if reg:
                return reg._dtype, True
            
    def setTypeScope(self, value: ScopeType):
        self.scopes.append(value)

    def getInLoop(self):
        length = len(self.scopes) - 1
        for i in range( length ):
            if self.scopes[length - i] == "while":
                return True
        return False

    def getInFunction(self):
        length = len(self.scopes) - 1
        for i in range( length ):
            if self.scopes[length - i] == "function":
                return True
        return False

    def setReturnType(self, rtype: DType, lineno: int):
        self.returnType = rtype
        self.returnLineno = lineno

    def getReturnType(self):
        rt = self.returnType
        rl = self.returnLineno
        self.returnType = None
        self.returnLineno = None
        return rt, rl

    def setFunction(self, name, dtype):
        self.functions[name] = dtype

    def getFunction(self, name):
        return self.functions.get(name)

has_errors = False

def error(lineno: int, msg: str):
    global has_errors
    print(f"{lineno}: {msg}")
    has_errors = True

def check_program(model):
    global has_errors
    
    has_errors = False
    env = Env()
    for n in model:
        _check(n, env)
    return not has_errors, model

def _binops(left: DType, op: BinOpType, right: DType) -> DType | None:
    if left != right:
        return None
    
    match left:
        case 'int':
            if op in ['+', '-', '*', '/']: return 'int'
            elif op in ['<', '<=', '>', '>=', '==', '!=']: return 'bool'
        case 'float':
            if op in ['+', '-', '*', '/']: return 'float'
            elif op in ['<', '<=', '>', '>=', '==', '!=']: return 'bool'
        case 'char':
            if op in ['<', '<=', '>', '>=', '==', '!=']: return 'bool'
        case 'bool':
            if op in ['==', '!=', '&&', '||']: return 'bool'
        case 'unit':
            if op in ['==', '!=', '&&', '||']: return 'bool'

    return None

def _unops(op: BinOpType, expr: DType) -> DType | None:
    match expr:
        case 'int':
            if op in ['+', '-']: return 'int'
        case 'float':
            if op in ['+', '-']: return 'float'
        case 'bool':
            if op in ['!']: return 'bool'

    return None

def _dtype(dtype: DType) -> DType | None:
    if dtype in ['int', 'float', 'char', 'bool', 'unit']:
        return dtype
    else:
        return None

@singledispatch
def _check(node: Node, env: Env):
    raise RuntimeError(f"{node} not checked")

rule = _check.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _check_literal(node: LiteralT, env: Env):
    dtype = None
    if isinstance(node, Integer): dtype = "int"
    if isinstance(node, Float): dtype = "float"
    if isinstance(node, Char): dtype = "char"
    if isinstance(node, Bool): dtype = "bool"
    if isinstance(node, Unit): dtype = "unit"

    node.p_type = dtype
    return dtype

@rule(BinOp)
def _check_binop(node: BinOp, env: Env):
    left_type = _check(node.left, env)
    right_type = _check(node.right, env)

    result_type = _binops(left_type, node.op, right_type)
    if not result_type:
        error(node.lineno, f"Unsupported operation: {left_type} {node.op} {right_type}")

    node.p_type = 'bool' if node.op in ['<', '>', '<=', '>=', '==', '!=', '&&', '||'] else right_type

    return result_type

@rule(UnOp)
def _check_unop(node: UnOp, env: Env):
    expr_type = _check(node.expr, env)

    result_type = _unops(node.op, expr_type)
    if not result_type:
        error(node.lineno, f"Unsupported operation: {node.op}{expr_type}")

    node.p_type = expr_type

    return result_type

@rule(PrintStatement)
def _check_print_statement(node: PrintStatement, env: Env):
    ty = _check(node.expr, env)
    node.p_type = ty

    if ty not in [*DataTypes, None]:
        error(node.lineno, f"Unsupported type {ty!r} with print")    

@rule(Location)
def _check_location(node: Location, env: Env):
    register = env.getRegister(node.name)
    if not register:
        error(node.lineno, f"{node.name} not defined!")

    node.p_type = register[0] if register else None

    return node.p_type

@rule(VarDefinition)
@rule(ConstDefinition)
def _check_definition(node: VarDefinition | ConstDefinition, env: Env):
    name = node.location.name

    has_error = False
    if name in ['break', 'const', 'continue', 'else', 'enum', 'import', 'false', 'func', 'if', 'let', 'match', 'return', 'struct', 'true', 'while', 'var']:
        error(node.lineno, f"{name} is a reserved word in wabbit language!")
        has_error = True

    if not has_error and env.getRegister(node.location.name):
        error(node.lineno, f"{node.location.name} already defined!")
        has_error = True

    if node.value:
        dtype = _check(node.value, env)
    else:
        dtype: DType = node.dtype

    if not dtype:
        has_error = True
    elif not _dtype(dtype):
        error(node.lineno, f'{dtype} is not a valid type')
        has_error = True

    if not has_error and node.value and node.dtype and dtype != node.dtype:
        error(node.lineno, f"Type error in initialization. {node.dtype} != {dtype}")

    env.createRegister(name, isinstance(node, VarDefinition), dtype)

@rule(AssignmentStatement)
def _check_assignmentstatement(node: AssignmentStatement, env: Env):
    loc_type = _check(node.location, env)
    val_type = _check(node.value, env)

    node.p_type = val_type

    has_error = False
    if not has_error and not env.isMutable(node.location.name):
        error(node.lineno, "Can't assign to const")
        has_error = True

    if not has_error and loc_type != val_type:
        error(node.lineno, f"Type error in assignment. {loc_type} != {val_type}")

@rule(IfStatement)
def _check_ifstatement(node: IfStatement, env: Env):
    cmp_type = _check(node.cmp, env)
    if cmp_type != 'bool':
        error(node.lineno, f"if test must be bool. Got {cmp_type}")

    env.setTypeScope('if')
    b_type = _check_blockstatement(node.block_if, env)

    if node.block_else:
        env.setTypeScope('else')
        _check_blockstatement(node.block_else, env)

    node.p_type = b_type

@rule(WhileStatement)
def _check_whilestatement(node: WhileStatement, env: Env):
    cmp_type = _check(node.cmp, env)
    if cmp_type and cmp_type != 'bool':
        error(node.lineno, f"while test must be bool. Got {cmp_type}")

    env.setTypeScope('while')
    _check(node.body, env)

@rule(Break)
@rule(Continue)
def _interpret_breakcontinue(node: Break | Continue, env: Env):
    if not env.getInLoop():
        error(node.lineno, f"{'break' if isinstance(node, Break) else 'continue'} used outside of while loop")

@rule(CompoundExpression)
def _check_compoundexpression(node: CompoundExpression, env: Env):
    env.setTypeScope('compoundexpression')
    env.newScope()

    for inst in node.instructions[:-1]:
        _check(inst, env)

    r_type = _check(node.instructions[-1], env)

    env.popScope()

    node.p_type = r_type

    return r_type;

@rule(BlockStatement)
def _check_blockstatement(node: BlockStatement, env: Env):
    env.newScope()

    has_error = False
    for inst in node.instructions:
        _check(inst, env)

        ret_type, ret_lineno = env.getReturnType()
        if not has_error and ret_lineno and ret_type != env.expectRetType:
            error(ret_lineno, f"Type error in return")
            has_error = True

    if isinstance(node.instructions[-1], LiteralT):
        node.p_type = node.instructions[-1].p_type
    else:
        node.p_type = None

    env.popScope(False)

    return node.p_type

@rule(FunctionParam)
def _check_functionparam(node: FunctionParam, env: Env):
    env.createRegister(node.name, True, node.dtype)
    return (node.dtype, )

@rule(FunctionDefinition)
def _check_functiondefinition(node: FunctionDefinition, env: Env):
    if not _dtype(node.ret):
        error(node.lineno, f'{node.ret} is not a valid type')
        return

    if env.getInFunction():
        error(node.lineno, f'Nested functions are not supported')
        return

    env.newScope()
    env.setTypeScope('function')

    dtype = ()
    for p in node.params:
        dtype += _check_functionparam(p, env)
    dtype += (node.ret, )

    env.expectRetType = node.ret
    env.setFunction(node.name, dtype)

    _check_blockstatement(node.body, env)

    env.popScope()
    env.expectRetType = None

@rule(FunctionCall)
def _check_functioncall(node: FunctionCall, env: Env):
    function_type = env.getFunction(node.name)

    has_error = False
    if not function_type:
        error(node.lineno, f'{node.name} not defined!')
        has_error = True

    if has_error: return None
    
    function_type = function_type
    params_type = function_type[:-1]
    return_type = function_type[-1]

    argstype = ()
    for a in node.args:
        argstype += (_check(a, env),)

    if len(params_type) != len(argstype):
        error(node.lineno, f"Wrong # arguments. Expected {len(params_type)}.")
        has_error = True

    if not has_error:
        for i in range( len(params_type) ):
            if params_type[i] != argstype[i]:
                error(node.lineno, f"Type error in argument {i+1}. Expected {params_type[i]}")
                break

    node.p_type = return_type

    return return_type

@rule(ReturnStatement)
def _check_returnstatement(node: ReturnStatement, env: Env):
    if not env.getInFunction():
        error(node.lineno, 'Return used outside of function')
        return None

    dtype = 'unit'
    if node.expr != None:
        dtype = _check(node.expr, env)

    env.setReturnType(dtype, node.lineno)

    return dtype