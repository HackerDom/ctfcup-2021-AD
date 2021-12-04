g++ -std=c++20 -g -fPIC -c -o lib.o lib.cpp
g++ -std=c++20 -g -fPIC -shared -o lib.so lib.o

