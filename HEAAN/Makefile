CC = g++
LDFLAGS = -lgmp -lntl -lm 
CXXFLAGS = -g -std=c++11 -pg 
LIBPATH = lib


# This sample should be run after make libHEAAN.a file in lib folder

# All Target
all: clean HEAAN run

lib:
	make -C $(LIBPATH)

# Tool invocations
HEAAN-o0: lib
	$(CC) $(CXXFLAGS) -L$(LIBPATH) -O0 ./run/run.cpp -lHEAAN -o $@ $(LDFLAGS)

# Tool invocations
HEAAN-o2: lib
	$(CC) $(CXXFLAGS) -O2 ./run/run.cpp ./lib/libHEAAN.a -o $@ $(LDFLAGS)
	
# Tool invocations
HEAAN-o3: lib
	$(CC) $(CXXFLAGS) -O3 ./run/run.cpp ./lib/libHEAAN.a -o $@ $(LDFLAGS)

# Other Targets
clean:
	rm -rf HEAAN-o0 HEAAN-o2 HEAAN-o3

run:
	./HEAAN
