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

  // interaction specifics
  int<lower=0> I; // number of interactions
  int<lower=0> interaction_levels; // how many Xs are interacted (usually 2)
  array[interaction_levels, I] int interaction_indexes; // indexes of interacting Xs
}
transformed data {
  matrix[N,I] interacted_X;

  //manually create interacted X values
  for(i in 1:I) {
    interacted_X[,i] = ones_vector(N);
  for(j in 1:interaction_levels) {
      interacted_X[,i] = interacted_X[,i] .* X[,interaction_indexes[j,i]];
    }
  }
}
parameters {
  vector[M] theta;
  vector[2] interaction_theta;
}
model {
  theta ~ normal(0,10);
  interaction_theta ~ normal(0,10);

  y ~ normal(X * theta + interacted_X * interaction_theta, 1);
}
generated quantities {
  matrix[N,I] interact_X;
  interact_X = interacted_X;
}
