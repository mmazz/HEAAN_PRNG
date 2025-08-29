#include "../src/HEAAN.h"
#include "utils.cpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

using namespace std;
using namespace NTL;

// Constantes para limitar valores mágicos
const long DEFAULT_LOG_N = 4;
const long DEFAULT_LOG_Q = 35;
const long DEFAULT_LOG_P = 25;
const unsigned int DEFAULT_MIN = 0;
const unsigned int DEFAULT_MAX = 8;
const size_t DEFAULT_LOOPS = 1;
const int DEFAULT_GAP_SHIFT = 0;
const size_t MAX_H = 64;

inline double norm2(std::complex<double> *vecInput, double *vecOutput,
                    size_t size) {
  double res = 0;
  double diff = 0;
  // Itero sobre el del input por si el del output por construccion quedo mas
  // grande
  for (size_t i = 0; i < size; i++) {
    diff = vecOutput[i] - vecInput[i].real();
    res += pow(diff, 2);
  }
  res = std::sqrt(res / size);
  return res;
}

int main(int argc, char *argv[]) {
  try {
    long logN = DEFAULT_LOG_N;
    long logQ = DEFAULT_LOG_Q;
    long logP = DEFAULT_LOG_P;
    unsigned int MIN = DEFAULT_MIN;
    unsigned int MAX = DEFAULT_MAX;
    size_t seed = DEFAULT_LOOPS;
    int gapShift = DEFAULT_GAP_SHIFT;

    if (argc > 1)
      logN = std::stol(argv[1]);
    if (argc > 2)
      logQ = std::stol(argv[2]);
    if (argc > 3)
      logP = std::stol(argv[3]);
    if (argc > 4)
      gapShift = std::stoi(argv[4]);
    if (argc > 5)
      MIN = std::stoi(argv[5]);
    if (argc > 6)
      MAX = std::stoi(argv[6]);
    if (argc > 7)
      seed = std::stoi(argv[7]);

    long h = pow(2, logN);
    if (h > MAX_H)
      h = MAX_H;

    size_t ringDim = (1 << logN);
    long logSlots = logN - 1;
    long slots = pow(2, logSlots);

    if (gapShift > 0) {
      slots = slots >> gapShift;
    }

    std::cout << "logN: " << logN << " logQ: " << logQ << " logP: " << logP
              << " Ringdim: " << ringDim << " slots: " << slots << std::endl;

    NTL::ZZ seed_NTL = ZZ(seed);
    NTL::SetSeed(seed_NTL);
    std::srand(seed);

    double *vals = new double[slots];
    for (uint32_t i = 0; i < slots; i++) {
      vals[i] = ((double)rand()) / RAND_MAX * MAX - MIN;
    }

    Context context(logN, logQ);
    SecretKey sk(logN, h);
    Scheme scheme(sk, context);

    Plaintext plain = scheme.encode(vals, slots, logP, logQ);
    Ciphertext cipher = scheme.encryptMsg(plain, seed_NTL);

    Plaintext golden_plain = scheme.decryptMsg(sk, cipher);
    complex<double> *golden_val = scheme.decode(golden_plain);

    double golden_norm = norm2(golden_val, vals, slots);

    return 0;

  } catch (const std::exception &e) {
    std::cerr << "Error: " << e.what() << std::endl;
    return 1;
  }
}
