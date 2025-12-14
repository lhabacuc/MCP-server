#include <pybind11/pybind11.h>
#include <cstdio>
#include <memory>
#include <array>
#include <string>

namespace py = pybind11;

#ifdef _WIN32
    #define popen _popen
    #define pclose _pclose
#endif
/*
//	libexec melhor lib para executar comandos no python kkkk##
*/
std::string	output_first;

std::string cmd(const std::string &command)
{
	std::array<char, 256> buffer;
	std::string result;

	FILE *pipe = popen(command.c_str(), "r");
	if (!pipe)
		throw std::runtime_error("Erro ao executar comando");

	while (fgets(buffer.data(), buffer.size(), pipe) != nullptr)
		result += buffer.data();
	pclose(pipe);
	return (result);
}

void entryponit()
{
	
}

void run(const std::string &command)
{
   output_first = cmd(command);
}

PYBIND11_MODULE(libexec, e)
{
    e.def("cmd", &cmd, "Executa um comando do sistema e retorna o stdout");
    e.def("entryponit", &entryponit);
    e.def("run", &run);
}

