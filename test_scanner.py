import sys
sys.path.insert(0, '.')
from src.core.analyzer import scan_rust, TokenType

def test_basic():
    text = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
    tokens, errors = scan_rust(text)
    print(f"Tokens count: {len(tokens)}")
    print(f"Errors count: {len(errors)}")
    for token in tokens:
        print(f"  {token.type.name:15} {token.lexeme:20} {token.start_line}:{token.start_col}-{token.end_line}:{token.end_col}")
    for err in errors:
        print(f"  ERROR line {err.line}:{err.column} {err.message}")
    expected_count = 20
    assert len(tokens) == expected_count, f"Expected {expected_count} tokens, got {len(tokens)}"
    assert len(errors) == 0, f"Expected no errors, got {len(errors)}"
    assert tokens[0].type == TokenType.KEYWORD
    assert tokens[0].lexeme == "let"
    assert tokens[2].type == TokenType.IDENTIFIER
    assert tokens[2].lexeme == "complex_num2"
    assert tokens[6].type == TokenType.IDENTIFIER
    assert tokens[6].lexeme == "num"
    assert tokens[7].type == TokenType.SEPARATOR
    assert tokens[7].lexeme == "::"
    assert tokens[8].type == TokenType.IDENTIFIER
    assert tokens[8].lexeme == "complex"
    assert tokens[9].type == TokenType.SEPARATOR
    assert tokens[9].lexeme == "::"
    assert tokens[10].type == TokenType.IDENTIFIER
    assert tokens[10].lexeme == "Complex"
    assert tokens[11].type == TokenType.SEPARATOR
    assert tokens[11].lexeme == "::"
    assert tokens[12].type == TokenType.KEYWORD
    assert tokens[12].lexeme == "new"
    assert tokens[13].type == TokenType.SEPARATOR
    assert tokens[13].lexeme == "("
    assert tokens[14].type == TokenType.FLOAT
    assert tokens[14].lexeme == "3.1"
    assert tokens[15].type == TokenType.SEPARATOR
    assert tokens[15].lexeme == ","
    assert tokens[17].type == TokenType.FLOAT
    assert tokens[17].lexeme == "-4.2"
    assert tokens[19].type == TokenType.END_OF_STATEMENT
    assert tokens[19].lexeme == ";"
    print("Test passed.")

if __name__ == "__main__":
    test_basic()