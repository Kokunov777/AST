import sys
sys.path.insert(0, '.')
from src.core.analyzer import scan_rust
from src.core.syntax_analyzer import parse_syntax

def test_syntax():
    text = "let complex_num2 = num::complex::Complex::new(3.1, -4.2);"
    tokens, lex_errors = scan_rust(text)
    print(f"Лексических ошибок: {len(lex_errors)}")
    
    syntax_errors = parse_syntax(tokens)
    print(f"Синтаксических ошибок: {len(syntax_errors)}")
    for err in syntax_errors:
        print(f"  Синтаксическая ошибка: {err.fragment} line {err.line}:{err.position} - {err.description}")
    
    # Ожидаем 0 ошибок
    assert len(syntax_errors) == 0, f"Ожидалось 0 синтаксических ошибок, получено {len(syntax_errors)}"
    print("Синтаксический анализ прошел успешно (нет ошибок).")
    
    # Тест с ошибкой
    text2 = "let complex_num2 = num::complex::Complex::new(3.1, -4.2)"  # отсутствует ;
    tokens2, _ = scan_rust(text2)
    errors2 = parse_syntax(tokens2)
    print(f"\nТест с ошибкой (отсутствует ';'): найдено {len(errors2)} ошибок")
    for err in errors2:
        print(f"  {err.description}")
    # Ожидаем хотя бы одну ошибку
    assert len(errors2) > 0, "Ожидалась синтаксическая ошибка"
    print("Тест с ошибкой прошел.")
    
    print("\nВсе тесты синтаксического анализатора прошли успешно.")

if __name__ == "__main__":
    test_syntax()