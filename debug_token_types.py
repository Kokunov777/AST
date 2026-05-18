import sys
sys.path.insert(0, '.')
from src.core.analyzer import scan_rust

text = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
tokens, errors = scan_rust(text)
for i, t in enumerate(tokens):
    print(f"{i}: lexeme='{t.lexeme}' token_type='{t.token_type}' type={t.type} code={t.code} is_error={t.is_error}")