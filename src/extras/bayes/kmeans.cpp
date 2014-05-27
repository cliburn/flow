#include "kmeans.hpp"
extern "C" {
#include "cluster.h"
}

// ublas::vector<int> calc_z(const ublas::matrix<double>& data, const ublas::vector<ublas::vector<double> >& centroids, const int n, const int k, const int p) {
//   ublas::vector<int> z(n);
//   ublas::vector<double> d(k);
//   for (int i=0; i<n; ++i) {
//     for (int j=0; j<k; ++j) {
//       d(j) = norm_2(centroids(j) - column(data, i));
//     }
//     z(i) = find(d.begin(), d.end(), *min_element(d.begin(), d.end())) - d.begin();
//   }
//   return z;
// }

// ublas::vector<ublas::vector<double> > calc_centroids(const ublas::matrix<double>& data, const ublas::vector<int>& z, const int n, const int k, const int p) {
//   ublas::vector<ublas::vector<double> > centroids(k);
//   std::vector<double> cluster;
//   for (int i=0; i<k; ++i) {
//     ublas::vector<double> s(p);
//     s.assign(ublas::zero_vector<double>(p));
//     int len = 0;
//     for (int j=0; j<n; ++j)
//       if (z[j]==i) {
// 	s += column(data, j);
// 	len++;
//       }
//     centroids(i) = s/len;
//   }

//   return centroids;
// }

// ublas::vector<ublas::vector<double> > kmeans(const ublas::matrix<double>& data, const int n, const int k, const int p, const double tol) {
//   ublas::vector<int> z(n);
//   ublas::vector<ublas::vector<double> > old_centroids(k);
//   ublas::vector<ublas::vector<double> > new_centroids(k);
//   // initialize with k random data points
//   std::vector<int> idx(n);
//   for (int i=0; i<n; ++i)
//     idx[i] = i;
//   random_shuffle(idx.begin(), idx.end());
//   for (int i=0; i<k; ++i)
//     old_centroids(i) = column(data, idx[i]);

//   double sep = tol + 1;
//   while (sep > tol) {
//     z = calc_z(data, old_centroids, n, k, p);
//     new_centroids = calc_centroids(data, z, n, k, p);
//     sep = 0.0;
//     for (int i=0; i<k; ++i)
//       sep += norm_2(old_centroids(i) - new_centroids(i));
//     old_centroids = new_centroids;
//   }
//   return new_centroids;
// }

ublas::vector<ublas::vector<double> > kmeans(const ublas::matrix<double>& data, const int n, const int k, const int p, const double tol) {
  double** _data = (double**) malloc(n*sizeof(double*));
  int** mask = (int**) malloc(n*sizeof(int*));
  double** cdata = (double**) malloc(n*sizeof(double*));
  int** cmask = (int**) malloc(n*sizeof(int*));
  for (int i=0; i<n; ++i) {
    _data[i] = (double*) malloc(p*sizeof(double));
    mask[i] = (int*) malloc(p*sizeof(int));
    cdata[i] = (double*) malloc(p*sizeof(double));
    cmask[i] = (int*) malloc(p*sizeof(int));
  }

  ublas::matrix<double> tdata = trans(data);

  for (int i=0; i<n; ++i)
    for (int j=0; j<p; j++) {
      _data[i][j] = tdata(i, j);
      mask[i][j] = 1;
    }

  double* weight = (double*) malloc(p*sizeof(double));
  for (int i=0; i<p; ++i)
    weight[i] = 1;

  int transpose = 0;
  int npass = 10;
  const char method = 'a';
  const char dist = 'e';
  int* cluster_id = (int*) malloc(n*sizeof(int));
  double error;
  int ifound = 0;
  
  kcluster(k, n, p, _data, mask, weight, transpose, npass, method, dist, cluster_id, &error, &ifound);

  getclustercentroids(k, n, p, _data, mask, cluster_id, cdata, cmask, 0, method);

  ublas::vector<ublas::vector<double> > result(k);
  for (int i=0; i<k; ++i) {
    ublas::vector<double> d(p);
    for (int j=0; j<p; ++j)
      d(j) = cdata[i][j];
    result(i) = d;
  }

  // free memory
  for (int i=0; i<n; ++i) {
    free(_data[i]);
    free(mask[i]);
    free(cdata[i]);
    free(cmask[i]);
  }

  free(_data);
  free(mask);
  free(cdata);
  free(cmask);
  free(weight);
  free(cluster_id);

  return result;
}
