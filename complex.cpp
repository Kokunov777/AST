#include <iostream>
#include <complex>

int main() {
    std::complex<double> z1(3.0, 4.0);
    std::complex<double> z2(1.0, 2.0);
    auto z3 = z1 * z2 + z1;
    std::cout << z3.real() << " " << z3.imag() << std::endl;
    return 0;
}