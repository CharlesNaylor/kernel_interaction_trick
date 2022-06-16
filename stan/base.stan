// for test0.1, with foreknowledge of the correct interaction
// hence no spike and slab
data {
	int<lower=1> N; // Number of data
	int<lower=1> M; // Number of covariates
	matrix[N, M] X;
	vector[N] y;

	// Interaction global scale params
	real<lower=0> c; // Intercept prior scale
	real m0; // Expected number of large slopes
}
transformed data {
  matrix[N,2] interacted_X; // interaction between (0, 8, 4), (2, 6, 5)

  interacted_X[,1] = X[,1] .* X[,9] .* X[,5];
  interacted_X[,2] = X[,3] .* X[,7] .* X[,6];
}
parameters {
  vector[M] theta;
  vector[2] interaction_theta;
}
model {
  theta ~ normal(0,10);
  interaction_theta ~ normal(0,1);

  y ~ normal(X * theta + interacted_X * interaction_theta, 1);
}
