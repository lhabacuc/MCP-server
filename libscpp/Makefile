#	by liedson habacuc http://github.com/lhabacuc
MODULE = libexec
SRC = libexecut.cpp

CXX = c++
FLAGS = -O3 -Wall -shared -std=c++17 -fPIC
INCLUDES = $(shell python3 -m pybind11 --includes)

TARGET = $(MODULE)$(shell python3-config --extension-suffix)

PREFIX_USER = $(HOME)/.local/lib/python$(shell python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")/site-packages

PREFIX_SUDO = /usr/local/lib/python$(shell python3 -c "import sys; print(f'{sys.version_info[0]}.{sys.version_info[1]}')")/dist-packages

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(FLAGS) $(INCLUDES) $(SRC) -o $(TARGET)

fclean:
	rm -f $(TARGET)

install_user: $(TARGET)
	mkdir -p $(PREFIX_USER)
	cp $(TARGET) $(PREFIX_USER)
	@echo "Instalado em $(PREFIX_USER)"

install_sudo: $(TARGET)
	sudo mkdir -p $(PREFIX_SUDO)
	sudo cp $(TARGET) $(PREFIX_SUDO)
	@echo "Instalado em $(PREFIX_SUDO)"

install: install_user

