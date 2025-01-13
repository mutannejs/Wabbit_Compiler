import re
from functools import singledispatch

from .model import *


class Env:
    def __init__(self):
        self.stack = {}

    # def newScope(self):
    #     self.stack.insert(0, {})

    # def popScope(self):
    #     self.stack.pop(0)

    def createRegister(self, name: str, data: Node | None):
        self.stack[name] = data

    def setRegister(self, name: str, data: Node):
        self.stack[name] = data

    def getRegister(self, name: str) -> Node | None:
        return self.stack.get(name)


class Context:
    _counter_t = 0
    _counter_l = 0
    def __init__(self):
        # You need some wabbit environment stuff for tracking names / objects
        self.env = Env()

        # List that holds all the declarations
        self.declarations = []

        # List that holds all the statements
        self.statements = []

        # usado com o break e com continue
        self.cmp_label = None
        self.return_label = None

    def type_transform(self, p_type: DType):
        match p_type:
            case 'bool': return 'int'
            case 'unit': return 'int*'
            case _: return p_type

    def new_temporary(self, c_type):
        '''
        Declare a new temporary variable
        '''
        Context._counter_t += 1
        name = f'_t{Context._counter_t}'
        self.declarations.append(f'\t{self.type_transform(c_type)} {name};')
        return name

    def new_label(self):
        '''
        Declare a new label
        '''
        Context._counter_l += 1
        return f'L{Context._counter_l}'

    def append(self, stmt, isLabel = False):
        self.statements.append( ('' if isLabel else '\t') + stmt )

    def str_env(self):
        registers = ''
        for k in self.env.stack.keys():
            registers += f'{self.env.stack[k]} {k};\n'
        return registers

    def __str__(self):
        return ("\n".join(self.declarations) + "\n\n" + \
                "\n".join(self.statements) + "\n")


def compile_program(model):
    ctx = Context()
    _compile(model, ctx)
    return ("#include <stdio.h>\n\n" +
            ctx.str_env() + '\n' +
            "int main() {\n" +
            str(ctx) +
            "\treturn 0;\n" +
            "}")


@singledispatch
def _compile(node: Node, ctx: Context):
    raise RuntimeError(f"{node} not compile")

rule = _compile.register

@rule(Integer)
@rule(Float)
@rule(Char)
@rule(Bool)
@rule(Unit)
def _compile_literal(node: LiteralT, ctx: Context):
    if isinstance(node, Bool) and node.value == True:
        return 1
    if isinstance(node, Bool) and node.value == False:
        return 0
    if isinstance(node, Unit):
        return 'NULL'
    if isinstance(node, Char):
        return repr(node.value) if node.value[0] != '\\' else f"'{node.value}'"
    return node.value

@rule(BinOp)
def _compile_binop(node: BinOp, ctx: Context):
    left_val = _compile(node.left, ctx)
    right_val = _compile(node.right, ctx)

    match node.op:
        case '+': resultval = f'{left_val} + {right_val}'
        case '-': resultval = f'{left_val} - {right_val}'
        case '/': resultval = f'{left_val} / {right_val}'
        case '*': resultval = f'{left_val} * {right_val}'
        case '<': resultval = f'{left_val} < {right_val}'
        case '>': resultval = f'{left_val} > {right_val}'
        case '<=': resultval = f'{left_val} <= {right_val}'
        case '>=': resultval = f'{left_val} >= {right_val}'
        case '==': resultval = f'{left_val} == {right_val}'
        case '!=': resultval = f'{left_val} != {right_val}'
        case '&&': resultval = f'{left_val} && {right_val}'
        case '||': resultval = f'{left_val} || {right_val}'

    tempname = ctx.new_temporary(node.p_type)
    ctx.append(f'{tempname} = {resultval};')
    return tempname

@rule(UnOp)
def _compile_unop(node: UnOp, ctx: Context):
    expr_value = _compile(node.expr, ctx)

    if node.op == '-':
        resultval = f'-{expr_value}'
    elif node.op == '!':
        resultval = f'!{expr_value}'
    else:
        resultval = f'+{expr_value}'

    tempname = ctx.new_temporary(node.p_type)
    ctx.append(f'{tempname} = {resultval};')
    return tempname

@rule(PrintStatement)
def _compile_print_statement(node: PrintStatement, ctx: Context):
    expr_value = _compile(node.expr, ctx)
    if not re.match(r'_t\d', repr(expr_value)):
        name = ctx.new_temporary(node.expr.p_type)
        ctx.append(f'{name} = {expr_value};')
        expr_value = name

    match node.expr.p_type:
        case 'bool': format_specifier = 'd'
        case 'char': format_specifier = 'c'
        case 'float': format_specifier = 'f'
        case 'int': format_specifier = 'd'

    if node.expr.p_type == 'unit':
        ctx.append(f'printf("()\\n");')
    else:
        end = '' if format_specifier == 'c' else '\\n'
        ctx.append(f'printf("%{format_specifier}{end}", {expr_value});')


@rule(Location)
def _compile_location(node: Location, ctx: Context):
    value = node.name
    return value

@rule(VarDefinition)
@rule(ConstDefinition)
def _interpret_definition(node: VarDefinition | ConstDefinition, ctx: Context):
    name = _compile_location(node.location, ctx)

    if node.value:
        value = _compile(node.value, ctx)
        dtype = ctx.type_transform(node.value.p_type)
    else:
        dtype = ctx.type_transform(node.dtype)

    if node.value:
        ctx.append(f'{name} = {value};')

    ctx.env.createRegister(name, dtype)

@rule(AssignmentStatement)
def _compile_assignmentstatement(node: AssignmentStatement, ctx: Context):
    value = _compile(node.value, ctx)
    ctx.append(f'{_compile_location(node.location, ctx)} = {value};')

@rule(IfStatement)
def _compile_ifstatement(node: IfStatement, ctx: Context):
    block_true_l = ctx.new_label()
    if node.block_else: block_false_l = ctx.new_label()
    return_l = ctx.new_label()

    cmp = _compile(node.cmp, ctx)
    ctx.append(f'if ({cmp}) goto {block_true_l};')
    ctx.append(f'goto {block_false_l if node.block_else else return_l};')

    ctx.append(f'{block_true_l}:', True)
    _compile_blockstatement(node.block_if, ctx)
    ctx.append(f'goto {return_l};')

    if node.block_else:
        ctx.append(f'{block_false_l}:', True)
        _compile_blockstatement(node.block_else, ctx)
        ctx.append(f'goto {return_l};')

    ctx.append(f'{return_l}:', True)

@rule(WhileStatement)
def _compile_whilestatement(node: WhileStatement, ctx: Context):
    cmp_l = ctx.new_label()
    body_l = ctx.new_label()
    return_l = ctx.new_label()

    return_l_temp = ctx.return_label
    ctx.return_label = return_l

    cmp_l_temp = ctx.cmp_label
    ctx.cmp_label = cmp_l

    ctx.append(f'{cmp_l}:', True)
    cmp = _compile(node.cmp, ctx)
    ctx.append(f'if ({cmp}) goto {body_l};')
    ctx.append(f'goto {return_l};')

    ctx.append(f'{body_l}:', True)
    _compile_blockstatement(node.body, ctx)
    ctx.append(f'goto {cmp_l};')

    ctx.append(f'{return_l}:', True)

    ctx.cmp_label = cmp_l_temp
    ctx.return_label = return_l_temp

@rule(Break)
@rule(Continue)
def _interpret_breakcontinue(node: Break | Continue, ctx: Context):
    if isinstance(node, Break):
        ctx.append(f'goto {ctx.return_label};')
    else:
        ctx.append(f'goto {ctx.cmp_label};')

@rule(CompoundExpression)
def _compile_compoundexpression(node: CompoundExpression, ctx: Context):
    # env.newScope()

    for inst in node.instructions[:-1]:
        _compile(inst, ctx)

    value = _compile( node.instructions[-1], ctx )
    
    # env.popScope()
    return value

@rule(BlockStatement)
def _compile_blockstatement(node: BlockStatement, ctx: Context):
    # ctx.env.newScope()

    for inst in node.instructions:
        _compile(inst, ctx)

    # ctx.env.popScope()