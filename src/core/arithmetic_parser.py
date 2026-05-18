"""
Синтаксический анализатор методом рекурсивного спуска для арифметических выражений.
Грамматика:
E → TA
A → ε | + TA | - TA
T → FB
B → ε | * FB | / FB | % FB
F → num | id | (E)
"""
from dataclasses import dataclass
from typing import List, Optional, Tuple
from .arithmetic_lexer import Token, TokenType, scan_arithmetic


@dataclass
class SyntaxError:
    line: int
    column: int
    message: str
    fragment: str


@dataclass
class Quadruple:
    """Тетрада (op, arg1, arg2, result)."""
    op: str
    arg1: str
    arg2: str
    result: str


class ArithmeticParser:
    def __init__(self, tokens: List[Token]):
        # Фильтруем пробелы
        self.tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        self.errors: List[SyntaxError] = []
        self.pos = 0
        self.temp_counter = 1
        self.quadruples: List[Quadruple] = []
        self.poliz: List[str] = []
        self.has_identifier = False
        # Стек значений для генерации тетрад
        self.value_stack: List[str] = []

    def parse(self) -> Tuple[bool, List[SyntaxError]]:
        """Запуск синтаксического анализа. Возвращает (успех, ошибки)."""
        self.errors.clear()
        self.pos = 0
        self.temp_counter = 1
        self.quadruples.clear()
        self.poliz.clear()
        self.has_identifier = False
        self.value_stack.clear()

        if not self.tokens or (len(self.tokens) == 1 and self.tokens[0].type == TokenType.END):
            self.errors.append(SyntaxError(1, 1, "Пустое выражение", ""))
            return False, self.errors

        success = self.E()

        if success and self.current_token().type != TokenType.END:
            token = self.current_token()
            self.errors.append(SyntaxError(
                token.start_line, token.start_col,
                f"Лишний символ '{token.lexeme}' после выражения",
                token.lexeme
            ))
            success = False

        # Если были ошибки, очищаем тетрады и ПОЛИЗ
        if not success:
            self.quadruples.clear()
            self.poliz.clear()

        return success, self.errors

    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return Token(TokenType.END, "", 1, 1, 1, 1)

    def match(self, expected_type: TokenType, lexeme: Optional[str] = None) -> bool:
        token = self.current_token()
        if token.type == expected_type:
            if lexeme is not None and token.lexeme != lexeme:
                return False
            self.pos += 1
            return True
        return False

    def consume(self, expected_type: TokenType, lexeme: Optional[str] = None,
                error_msg: str = "") -> bool:
        if self.match(expected_type, lexeme):
            return True
        token = self.current_token()
        if not error_msg:
            expected = f"'{lexeme}'" if lexeme else expected_type.name
            error_msg = f"Ожидается {expected}, но получено '{token.lexeme}'"
        self.errors.append(SyntaxError(
            token.start_line, token.start_col,
            error_msg, token.lexeme
        ))
        return False

    # Грамматические правила с семантическими действиями

    def E(self) -> bool:
        """E → TA"""
        if not self.T():
            return False
        if not self.A():
            return False
        return True

    def A(self) -> bool:
        """A → ε | + TA | - TA"""
        token = self.current_token()
        if token.type in (TokenType.OPERATOR_PLUS, TokenType.OPERATOR_MINUS):
            op = token.lexeme
            self.pos += 1
            # Сохраняем левый операнд (уже на стеке)
            if not self.T():
                return False
            # Правый операнд теперь на вершине стека, левый под ним
            if len(self.value_stack) >= 2:
                arg2 = self.value_stack.pop()
                arg1 = self.value_stack.pop()
                temp = self._gen_temp()
                self.quadruples.append(Quadruple(op, arg1, arg2, temp))
                self.value_stack.append(temp)
                self.poliz.append(op)
            else:
                # Недостаточно операндов (ошибка)
                self.errors.append(SyntaxError(
                    token.start_line, token.start_col,
                    f"Недостаточно операндов для оператора '{op}'",
                    token.lexeme
                ))
                return False
            # Рекурсивно обрабатываем продолжение
            if not self.A():
                return False
        return True

    def T(self) -> bool:
        """T → FB"""
        if not self.F():
            return False
        if not self.B():
            return False
        return True

    def B(self) -> bool:
        """B → ε | * FB | / FB | % FB"""
        token = self.current_token()
        if token.type in (TokenType.OPERATOR_MUL, TokenType.OPERATOR_DIV,
                          TokenType.OPERATOR_MOD):
            op = token.lexeme
            self.pos += 1
            if not self.F():
                return False
            if len(self.value_stack) >= 2:
                arg2 = self.value_stack.pop()
                arg1 = self.value_stack.pop()
                temp = self._gen_temp()
                self.quadruples.append(Quadruple(op, arg1, arg2, temp))
                self.value_stack.append(temp)
                self.poliz.append(op)
            else:
                self.errors.append(SyntaxError(
                    token.start_line, token.start_col,
                    f"Недостаточно операндов для оператора '{op}'",
                    token.lexeme
                ))
                return False
            if not self.B():
                return False
        return True

    def F(self) -> bool:
        """F → num | id | (E)"""
        token = self.current_token()
        if token.type == TokenType.INTEGER:
            self.pos += 1
            # Для целого числа просто кладем его значение на стек
            self.value_stack.append(token.lexeme)
            self.poliz.append(token.lexeme)
            return True
        elif token.type == TokenType.IDENTIFIER:
            self.has_identifier = True
            self.pos += 1
            self.value_stack.append(token.lexeme)
            self.poliz.append(token.lexeme)
            return True
        elif token.type == TokenType.LPAREN:
            self.pos += 1
            if not self.E():
                return False
            if not self.consume(TokenType.RPAREN, ")", "Ожидается ')'"):
                return False
            return True
        else:
            self.errors.append(SyntaxError(
                token.start_line, token.start_col,
                f"Ожидается число, идентификатор или '('",
                token.lexeme
            ))
            return False

    def _gen_temp(self) -> str:
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def get_quadruples(self) -> List[Quadruple]:
        return self.quadruples

    def get_poliz(self) -> List[str]:
        return self.poliz

    def has_identifiers(self) -> bool:
        return self.has_identifier


def parse_arithmetic(text: str) -> Tuple[bool, List[SyntaxError], List[Quadruple],
                                         List[str], bool]:
    """
    Полный анализ арифметического выражения.
    Возвращает:
    - успех (bool)
    - список ошибок синтаксиса
    - список тетрад (если успех)
    - ПОЛИЗ (если успех)
    - есть ли идентификаторы
    """
    tokens, lex_errors = scan_arithmetic(text)
    if lex_errors:
        errors = [SyntaxError(err.line, err.column, err.message, "")
                  for err in lex_errors]
        return False, errors, [], [], False

    parser = ArithmeticParser(tokens)
    success, errors = parser.parse()
    quadruples = parser.get_quadruples() if success else []
    poliz = parser.get_poliz() if success else []
    return success, errors, quadruples, poliz, parser.has_identifiers()


def evaluate_poliz(poliz: List[str]) -> Optional[int]:
    """
    Вычисление значения выражения, представленного в ПОЛИЗ.
    Работает только для целых чисел и операторов + - * / %.
    Возвращает целое число или None при ошибке (деление на ноль).
    """
    stack = []
    for token in poliz:
        if token.isdigit() or (token[0] == '-' and token[1:].isdigit()):
            stack.append(int(token))
        elif token in {'+', '-', '*', '/', '%'}:
            if len(stack) < 2:
                return None
            b = stack.pop()
            a = stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                if b == 0:
                    return None
                stack.append(a // b)  # целочисленное деление
            elif token == '%':
                if b == 0:
                    return None
                stack.append(a % b)
        else:
            # идентификатор или что-то еще
            return None
    if len(stack) == 1:
        return stack[0]
    return None