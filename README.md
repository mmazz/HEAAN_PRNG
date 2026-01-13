# HEAAN

- This version is Asiacrypt2017 implementation. https://www.researchgate.net/publication/321501858_Advances_in_Cryptology_-_ASIACRYPT_2017_23rd_International_Conference_on_the_Theory_and_Applications_of_Cryptology_and_Information_Security_Hong_Kong_China_December_3-7_2017_Proceedings_Part_I

- For the latest version of HEAAN please go to https://github.com/snucrypto/HEAAN

- You can also find this version in https://github.com/snucrypto/HEAAN/releases/tag/1.0

## PRNG Control

We add new encrypt method to select a seed:
```
Ciphertext Scheme::encryptMsg(Plaintext& msg, ZZ seed)
```

### Example

```
NTL::ZZ seed = ZZ(1);
Ciphertext cipher = scheme.encryptMsg(plain, seed);
```

## Dependencies

- lzip
- GMP
```
curl -O https://ftp.gnu.org/gnu/gmp/gmp-6.1.2.tar.lz
tar --lzip -xvf gmp-6.1.2.tar.lz
( \

  cd ./gmp-6.1.2 || exit; \
  ./configure; \
  make; \
  make check; \
  sudo make install; \
  cd ..; \
)
rm gmp-6.1.2.tar.lz
rm -rf gmp-6.1.2
```
- NTL
```
curl -O https://libntl.org/ntl-10.5.0.tar.gz
tar -xvf ntl-10.5.0.tar.gz
( \
  cd ./ntl-10.5.0/src || exit; \
  ./configure NTL_THREADS=on NTL_THREAD_BOOST=on NTL_EXCEPTIONS=on SHARED=on NTL_STD_CXX11=on NTL_SAFE_VECTORS=off TUNE=generic; \
  make; \
  make check; \
  sudo make install; \
  cd ../.. \
)
rm ntl-10.5.0.tar.gz
rm -rf ntl-10.5.0
```  


## Instalation

cd HEAAN/lib
make -j$(nproc)


# License
Copyright (c) by CryptoLab inc. This program is licensed under a Creative Commons Attribution-NonCommercial 3.0 Unported License. You should have received a copy of the license along with this work. If not, see http://creativecommons.org/licenses/by-nc/3.0/.
