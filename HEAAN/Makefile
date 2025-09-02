CC = g++
LDFLAGS = -lgmp -lntl -lm 
CXXFLAGS = -pg -g -std=c++11 -O0
LIBPATH = lib

# Define the test source directory
SRCDIR = run

# Use a wildcard to find all source files in the specified directory
SRCS = $(wildcard $(SRCDIR)/*.cpp)

# Use patsubst to create the list of binaries from the source file paths
# The syntax is $(patsubst pattern,replacement,text)
# We remove the directory and the .cpp extension
BINS = $(patsubst $(SRCDIR)/%.cpp,%,$(SRCS))

# The 'all' rule is the default target and is what 'make' will build by default
all: $(BINS)

# The pattern rule to compile each source file into its own binary
# This is a powerful feature that avoids repeating rules for each file
$(BINS): %: $(SRCDIR)/%.cpp
	$(CC) $(CXXFLAGS) -L$(LIBPATH) $< -lHEAAN -o ./bin/$@ $(LDFLAGS)

lib:
	make -C $(LIBPATH)

.PHONY: clean
clean:
	rm -f $(BINS)

