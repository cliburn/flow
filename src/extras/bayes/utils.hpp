#ifndef UTILS_HPP
#define UTILS_HPP

// #include "common.hpp"
#include <iostream>
#include <fstream>
#include <boost/numeric/bindings/traits/ublas_matrix.hpp>
using std::cout;
using std::cerr;
using std::cin;

namespace ublas = boost::numeric::ublas;

std::vector<int> argsort(const ublas::vector<double>& x);
std::vector<int> find_all(const ublas::vector<int>& x, const int value);
ublas::matrix<double> read_data(std::string filename, int n, int p);
ublas::vector<ublas::vector<double> > read_mu(std::string filename, int k, int p);

void write_matrix(const std::string& filename, ublas::matrix<int>& data);
void write_matrix(const std::string& filename, ublas::matrix<double>& data);

void write_vec(const std::string& filename, const std::vector<ublas::vector<int> >& data);
void write_vec(const std::string& filename, const std::vector<ublas::vector<double> >& data);
void write_vec_vec(const std::string& filename, const std::vector<ublas::vector<ublas::vector<double> > >& data);
void write_vec_mat(const std::string& filename, const std::vector<ublas::vector<ublas::matrix<double> > >& data);
std::string int2str(int n);
#endif
