CXX = g++
CXXFLAGS = -std=c++17 -Wall -IAlgoritmSPH/include

# Archivos fuente
SRC = AlgoritmSPH/main.cpp $(wildcard AlgoritmSPH/src/*.cpp AlgoritmSPH/src/*/*.cpp AlgoritmSPH/src/*/*/*.cpp)

# Directorio para objetos
OBJDIR = build
OBJ = $(patsubst %.cpp,$(OBJDIR)/%.o,$(SRC))

# Ejecutable
TARGET = simulacion

all: $(TARGET)

# Generar ejecutable en la raíz
$(TARGET): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Regla genérica para compilar .cpp a .o
$(OBJDIR)/%.o: %.cpp | $(OBJDIR)
	mkdir -p $(dir $@)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Crear directorio de objetos
$(OBJDIR):
	mkdir -p $(OBJDIR)

# Limpiar objetos y ejecutable
clean:
	rm -rf $(OBJDIR) $(TARGET) Output/simulation/*.txt Output/tests/*.output
