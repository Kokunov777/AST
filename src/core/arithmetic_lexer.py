"""
Лексический анализатор для арифметических выражений по грамматике:
E → TA
A → ε | + TA | - TA
T → FB
B → ε | * FB | / FB | % FB
F → num | id | (E)
id → letter {letter | digit | _}
num → digit {digit}
"""
import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional


class TokenType(Enum):
    INTEGER = 1          # целое число
    IDENTIFIER = 2       # идентификатор (буквы, цифры, _)
    OPERATOR_PLUS = 3    # +
    OPERATOR_MINUS = 4   # -
    OPERATOR_MUL = 5     # *
    OPERATOR_DIV = 6     # /
    OPERATOR_MOD = 7     # %
    LPAREN = 8           # (
    RPAREN = 9           # )
    WHITESPACE = 10      # пробелы, табы
    ERROR = 11           # недопустимый символ
    END = 12             # конец входной строки


@dataclass
class Token:
    type: TokenType
    lexeme: str
    start_line: int
    start_col: int
    end_line: int
    end_col: int


@dataclass
class LexerError:
    line: int
    column: int
    message: str


class ArithmeticLexer:
    def __init__(self):
        self.tokens: List[Token] = []
        self.errors: List[LexerError] = []
        self.line = 1
        self.col = 1
        self.pos = 0
        self.text = ""
        self.length = 0

    def analyze(self, text: str) -> Tuple[List[Token], List[LexerError]]:
        self.text = text
        self.length = len(text)
        self.tokens.clear()
        self.errors.clear()
        self.line = 1
        self.col = 1
        self.pos = 0

        while self.pos < self.length:
            self._process_next()

        # Добавляем токен конца строки
        self.tokens.append(Token(TokenType.END, "", self.line, self.col, self.line, self.col))
        return self.tokens, self.errors

    def _process_next(self):
        ch = self.text[self.pos]
        start_line = self.line
        start_col = self.col

        # Новые строки
        if ch == '\n':
            self.line += 1
            self.col = 1
            self.pos += 1
            return

        # Пробельные символы
        if ch in ' \t\r':
            j = self.pos
            while j < self.length and self.text[j] in ' \t\r':
                j += 1
            lexeme = self.text[self.pos:j]
            self.tokens.append(Token(TokenType.WHITESPACE, lexeme, start_line, start_col,
                                     self.line, self.col + (j - self.pos) - 1))
            self.col += j - self.pos
            self.pos = j
            return

        # Числа
        if ch.isdigit():
            j = self.pos
            while j < self.length and self.text[j].isdigit():
                j += 1
            lexeme = self.text[self.pos:j]
            self.tokens.append(Token(TokenType.INTEGER, lexeme, start_line, start_col,
                                     self.line, self.col + (j - self.pos) - 1))
            self.col += j - self.pos
            self.pos = j
            return

        # Идентификаторы (буква или _)
        if ch.isalpha() or ch == '_':
            j = self.pos
            while j < self.length and (self.text[j].isalnum() or self.text[j] == '_'):
                j += 1
            lexeme = self.text[self.pos:j]
            self.tokens.append(Token(TokenType.IDENTIFIER, lexeme, start_line, start_col,
                                     self.line, self.col + (j - self.pos) - 1))
            self.col += j - self.pos
            self.pos = j
            return

        # Операторы и скобки
        if ch == '+':
            self._add_token(TokenType.OPERATOR_PLUS, ch, start_line, start_col)
            return
        if ch == '-':
            self._add_token(TokenType.OPERATOR_MINUS, ch, start_line, start_col)
            return
        if ch == '*':
            self._add_token(TokenType.OPERATOR_MUL, ch, start_line, start_col)
            return
        if ch == '/':
            self._add_token(TokenType.OPERATOR_DIV, ch, start_line, start_col)
            return
        if ch == '%':
            self._add_token(TokenType.OPERATOR_MOD, ch, start_line, start_col)
            return
        if ch == '(':
            self._add_token(TokenType.LPAREN, ch, start_line, start_col)
            return
        if ch == ')':
            self._add_token(TokenType.RPAREN, ch, start_line, start_col)
            return

        # Неизвестный символ
        self.errors.append(LexerError(self.line, self.col, f"Недопустимый символ '{ch}'"))
        self.pos += 1
        self.col += 1

    def _add_token(self, token_type: TokenType, lexeme: str, start_line: int, start_col: int):
        self.tokens.append(Token(token_type, lexeme, start_line, start_col,
                                 self.line, self.col))
        self.pos += 1
        self.col += 1


def scan_arithmetic(text: str) -> Tuple[List[Token], List[LexerError]]:
    """
    Лексический анализатор для арифметических выражений.
    Возвращает список токенов и список ошибок.
    """
    lexer = ArithmeticLexer()
    return lexer.analyze(text)