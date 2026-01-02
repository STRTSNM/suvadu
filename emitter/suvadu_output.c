#include <stdio.h>

int main() {
    long long n = 0;
    long long s = 0;
    long long i = 0;

    n = 99999; // Increased for a real speed test
    for (i = 0; i < n; i++) {
        s += i;
    }

    printf("Result: %lld\n", s);
    return 0;
}
