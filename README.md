# Benchmarking label error detection algorithms for multi-label classification

A DVC project for running benchmarks on the quality of label scores for multi-label classification with synthetic data.

## Instructions

1. Clone the repo
2a [*Optional*]. Open the repo in a devcontainer
2b. Install the requirements with:
```bash
pip install -r requirements.txt
```
3. Run the pipeline with:

```bash
dvc repro
```

  - The pipeline has several stages:

  ```bash
  $ dvc dag
    +--------------+         +-----------------+
    | make_dataset |         | configure_train |
    +--------------+***      +-----------------+
            *          *****          *
            *               ****      *
            *                   ***   *
  +------------------+            +-------+
  | get_avg_accuracy |            | train |
  +------------------+            +-------+
            *                         *
            *                         *
            *                         *
    +-------------+           +---------------+
    | group_stats |           | score_classes |
    +-------------+           +---------------+
                                      *
                                      *
                                      *
                                +-----------+
                                | aggregate |
                                +-----------+
                                      *
                                      *
                                      *
                              +--------------+
                              | rank_metrics |
                              +--------------+
                                      *
                                      *
                                      *
                              +--------------+
                              | plot_metrics |
                              +--------------+
  +----------------+
  | plot_avg_trace |
  +----------------+
  ```

  A description of each stage is given below.
  ```
  $ dvc stage list
  make_dataset      Create groups of datasets of different sizes & number of classes.
  configure_train   Configure the model training pipeline.
  train             Train models and get out-of-sample predicted probabilities on the training sets.
  get_avg_accuracy  Get model performance metrics on test sets, with and without label errors.
  group_stats       Summarize model performance metrics for each group of datasets.
  score_classes     Compute class label quality scores for each example in a dataset.
  aggregate         Aggregate class label quality scores for all classes into a single score.
  rank_metrics      Compute label error detection metrics for aggregated scores.
  plot_metrics      Plot the label error detection and ranking metrics for the aggregated scores.
  plot_avg_trace    Plot average traces of noise matrices used for noisy label generation.
  ```


  - The stages have various output files and directories. This is best viewed with `dvc dag -o`. Ignoring most of the intermediate files, the most relevant files are:
    - data/accuracy/results_group.csv: Statistics of model performance metrics for each group of datasets.
    - data/scores/results.csv: Class label quality scores for each example in each dataset.
    - data/scores/metrics.csv: Statistics of label error detection and ranking metrics for each group of datasets.


4. Inspect the synthetic datasets in the `notebooks/inspect_generated_data.ipynb` notebook.
5. Inspect the results in the `notebooks/inspect_score_results.ipynb` notebook.

## Aggregator methods

Along with the typical `np.mean`, `np.median`, `np.min`, `np.max` aggregators, we also implement several methods found in `src/evaluation/aggregate.py`:

- `softmin_pooling`
- `log_transform_pooling`
- `cumulative_average`
- `simple_moving_average`
- `exponential_moving_average`
- `weighted_cumulative_average`
