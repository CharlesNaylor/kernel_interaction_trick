# Working through the Kernel Interaction Trick paper

I read this one a while ago. The paper discusses a method of inducing sparsity in a regression using GPs.

I wonder if I can't also use it to improve stability on models with a high degree of hierarchy, e.g. 3 or more groupings.

## Step 1

Prove out work done in the paper on a randomly generated dataset

## Step 2

Test general high N grouping on a randomly generated dataset

## Step 3

Try some real (or semi-real) data. E.g. the dataset I made for Hierarchical ZIP on Ginnie Mae

## Worklog

- 2022-06-16: fdc8a68. skim\_sq took 18 hours to run against test0.1 datagen config. I forgot to capture the samples, though, so no additional info on accuracy against true params
