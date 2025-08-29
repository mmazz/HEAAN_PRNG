# Compiler and flags
CXX      := g++
CXXFLAGS := -g -pg -std=c++11 -pthread -I../src -I/usr/local/include
LDFLAGS  := -L. -lHEAAN -lntl -lgmp -lm

# Directories
SRC_DIR  := ../src
OBJ_DIR  := build

# Sources and objects
SRCS     := $(wildcard $(SRC_DIR)/*.cpp)
OBJS     := $(patsubst $(SRC_DIR)/%.cpp,$(OBJ_DIR)/%.o,$(SRCS))

# Targets
LIB      := libHEAAN.a
TARGET   := HEAAN

.PHONY: all clean

# Default rule
all: $(LIB) 

# Build static library
$(LIB): $(OBJS)
	ar rcs $@ $^

# Build main program linking against libHEAAN
$(TARGET): $(MAIN) $(LIB)
	$(CXX) $(CXXFLAGS) -o $@ $(MAIN) $(LDFLAGS)

# Compile .cpp to .o
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp | $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Ensure build directory exists
$(OBJ_DIR):
	mkdir -p $(OBJ_DIR)

# Cleanup
clean:
	rm -rf $(OBJ_DIR) $(TARGET) $(LIB)

