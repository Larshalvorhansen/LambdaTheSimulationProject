#include <stdint.h>
#include <iostream>

int main() {
  uint64_t state = 1u << 31;
  for (int i = 0; i < 32; ++i) {
    for (int j = 64; j--;) {
      std::cout << char(state >> j & 1 ? 'O' : '.');
    }
    std::cout << '\n';
    state = (state >> 1) ^ (state | state << 1);
  }
}