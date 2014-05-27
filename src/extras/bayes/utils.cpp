#include "utils.hpp"
#include <utility>
#include <algorithm>
using std::make_pair;

std::vector<int> argsort(const ublas::vector<double>& x) {
  //! returns idx of reverse sort - like reverse(argsort(x))
  std::vector<std::pair<double, int> > v;
  for (unsigned i=0; i<x.size(); ++i)
    v.push_back(make_pair(x[i], i));
  
  std::sort(v.begin(), v.end());
  std::vector<int> idx;
  for (unsigned i=0; i<v.size(); ++i)
    idx.push_back(v[i].second);

  return idx;
}

std::vector<int> find_all(const ublas::vector<int>& x, const int value) {
  std::vector<int> idx;
  for (size_t i=0; i<x.size(); ++i)
    if (x(i) == value)
      idx.push_back(i);
  return idx;
}

ublas::matrix<double> read_data(std::string filename, int rows, int cols) {
  std::ifstream fin(filename.c_str());
  if (!fin) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  ublas::matrix<double> x(rows, cols);
  for (int i=0; i<rows; ++i)
    for (int j=0; j<cols; ++j)
      fin >> x(i, j);
  
  fin.close();
  return trans(x);
}

ublas::vector<ublas::vector<double> > read_mu(std::string filename, int k, int p) {
  std::ifstream fin(filename.c_str());
  if (!fin) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  ublas::vector<ublas::vector<double> > mu(k);
  for (int i=0; i<k; ++i) {
    mu(i).resize(p);
    for (int j=0; j<p; ++j)
      fin >> mu(i)(j);
  }
  
  fin.close();
  return mu;
}

void write_matrix(const std::string& filename, ublas::matrix<int>& data) {
  std::ofstream fout(filename.c_str(), std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size1(); ++i) {
    for (size_t j=0; j<data.size2(); ++j) {
      fout << data(i, j) << " ";
    }
    fout <<  "\n";
  }
  fout.close();
}
  
void write_matrix(const std::string& filename, ublas::matrix<double>& data) {
  std::ofstream fout(filename.c_str(), std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size1(); ++i) {
    for (size_t j=0; j<data.size2(); ++j) {
      fout << data(i, j) << " ";
    }
    fout <<  "\n";
  }
  fout.close();
}
  
void write_vector(const ublas::vector<double>& v, std::string filename) {
  std::ofstream fout(filename.c_str(), std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<v.size(); ++i) {
    fout << v[i] << "\n";
  }
  fout.close();
}

void write_vec(const std::string& filename, const std::vector<ublas::vector<double> >& data) {
  std::ofstream fout(filename.c_str()); //! , std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size(); ++i) {
    for (size_t j=0; j<data[i].size(); ++j) { // data[i] is a ublas::vector<double>
      fout << data[i](j) << " ";
    }
    fout << "\n";
  }
}

void write_vec(const std::string& filename, const std::vector<ublas::vector<int> >& data) {
  std::ofstream fout(filename.c_str()); //! , std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size(); ++i) {
    for (size_t j=0; j<data[i].size(); ++j) { // data[i] is a ublas::vector<double>
      fout << data[i](j) << " ";
    }
    fout << "\n";
  }
}

void write_vec_vec(const std::string& filename, const std::vector<ublas::vector<ublas::vector<double> > >& data) {
  std::ofstream fout(filename.c_str()); //!, std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size(); ++i) {
    for (size_t j=0; j<data[i].size(); ++j) { // data[i] is a ublas::vector<ublas::vector<double>
      for (size_t r=0; r<data[i](j).size(); ++r) { // data[i](j) is a ublas::vector<double>
	fout << data[i](j)(r) << " ";
      }
      fout << "\n";
    }
    fout << "\n";
  }
}
  
void write_vec_mat(const std::string& filename, const std::vector<ublas::vector<ublas::matrix<double> > >& data) {
  std::ofstream fout(filename.c_str()); //! , std::ios::app);
  if (!fout) {
    cerr << "Cannot open file " << filename << "\n";
    exit(1);
  }
  for (size_t i=0; i<data.size(); ++i) {
    for (size_t j=0; j<data[i].size(); ++j) { // data[i] is a ublas::vector<ublas::matrix<double>
      for (size_t r=0; r<data[i](j).size1(); ++r) { // data[i](j) is a ublas::matrix<double>
	for (size_t s=0; s<data[i](j).size2(); ++s) { // data[i](j) is a ublas::matrix<double>
	  fout << data[i](j)(r, s) << " ";
	}
	fout << "\n";
      }
      fout << "\n";
    }
    fout << "\n";
  }
}

std::string int2str(int n) {
  // convert int to string
  std::stringstream ss;
  std::string str;
  ss << n;
  ss >> str;
  return str;
}

