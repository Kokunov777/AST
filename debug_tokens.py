import sys
sys.path.insert(0, '.')
from src.core.analyzer import scan_rust, TokenType

code = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
tokens, errors = scan_rust(code)
print("Токены:")
for t in tokens:
    print(f"  {t.type.name:15} '{t.lexeme}' ({t.start_line}:{t.start_col}-{t.end_line}:{t.end_col})")
print("Ошибки:", errors)