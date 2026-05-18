typedef struct {
    double re;
    double im;
} Complex;

Complex mul(Complex a, Complex b) {
    Complex r;
    r.re = a.re * b.re - a.im * b.im;
    r.im = a.re * b.im + a.im * b.re;
    return r;
}

Complex add(Complex a, Complex b) {
    Complex r;
    r.re = a.re + b.re;
    r.im = a.im + b.im;
    return r;
}

int main() {
    Complex z1 = {3.0, 4.0};
    Complex z2 = {1.0, 2.0};
    Complex z3 = add(mul(z1, z2), z1);
    // printf опустим
    return 0;
}