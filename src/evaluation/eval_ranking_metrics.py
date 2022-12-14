import numpy as np
import pandas as pd
from src.evaluation.metrics import average_precision_at_k, lift_at_k
from sklearn.metrics import average_precision_score, roc_auc_score
import pathlib
from tqdm import tqdm

SCORE_DIR = pathlib.Path("data/scores")


def compute_ranking_metrics(scores, mask, k) -> dict:
    """Compute ranking metrics for a set of scores and a mask of errors.

    Parameters
    ----------
    scores : np.ndarray
        Array of multilabel quality scores.

    mask : np.ndarray
        Array of boolean values indicating whether a given example has a label error.

    k : int
        @k value for computing lift and AP metrics.
    """
    assert scores.shape == mask.shape, "scores and mask must have the same shape"
    assert (
        k <= scores.shape[0]
    ), "k must be less than or equal to the number of examples"
    metrics_dict = {
        "auroc": roc_auc_score(mask, scores),
        "lift_at_100": lift_at_k(mask, scores, k=100),
        "lift_at_num_errors": lift_at_k(mask, scores, k=k),
        "auprc": average_precision_score(mask, scores),
        "ap_at_100": average_precision_at_k(mask, scores, k=100),
        "ap_at_num_errors": average_precision_at_k(mask, scores, k=k),
    }
    return metrics_dict


def update_experiment_metrics(
    experiment: dict, scores: np.ndarray, mask: np.ndarray, suffix: str, k: int
) -> None:
    if len(suffix) > 0:
        assert suffix.startswith(
            "_"
        ), "suffix must start with an underscore to be appended to metric names"

    inv_scores = 1 - scores
    metrics_dict = compute_ranking_metrics(inv_scores, mask, k)

    experiment.update({f"{key}{suffix}": value for key, value in metrics_dict.items()})


def main():
    df = pd.read_pickle(SCORE_DIR / "scores.pkl")

    # New experiments
    experiments_with_metrics = []
    for experiment in tqdm(df.to_dict(orient="records"), miniters=len(df) // 25):
        label_errors_mask = experiment.pop("label_errors_mask")
        two_label_errors_mask = experiment.pop("two_label_errors_mask")
        three_label_errors_mask = experiment.pop("three_label_errors_mask")
        num_two_label_errors = experiment.pop("num_two_label_errors")
        num_three_label_errors = experiment.pop("num_three_label_errors")
        scores = experiment.pop("scores")
        num_errors = experiment["num_errors"]
        for mask_name_suffix, mask, k in zip(
            ["", "_two", "_three"],
            [label_errors_mask, two_label_errors_mask, three_label_errors_mask],
            [num_errors, num_two_label_errors, num_three_label_errors],
        ):
            update_experiment_metrics(experiment, scores, mask, mask_name_suffix, k)
        experiments_with_metrics.append(experiment)

    df_with_metrics = pd.DataFrame(experiments_with_metrics)

    df_with_metrics.to_csv(SCORE_DIR / "results.csv", index=False)


if __name__ == "__main__":
    main()
