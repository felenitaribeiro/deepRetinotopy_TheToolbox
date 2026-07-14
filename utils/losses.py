"""Loss functions for training.

visualCoord losses take (pred, target, R2, mask) with (N, 2) normalized Cartesian
coordinates; the pRF-size loss takes the (N,) scalar prediction/target. R2 is the
per-vertex variance explained (used as a weight) and mask is the per-vertex
validity boolean. LOSSES / PRF_LOSSES map the --loss / --prf_loss CLI name to the
function (used by main/train.py).
"""
import torch
import torch.nn.functional as F

EPS = 1e-8


def _weighted_mean(per_vertex, weight):
    return (weight * per_vertex).sum() / (weight.sum() + EPS)


def loss_euclidean(pred, target, R2, mask):
    """R2-weighted mean Euclidean distance in Cartesian visual-field space
    (weighted AVERAGE: divided by the sum of weights)."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    return _weighted_mean(dist, R2 * mask.float())


def loss_weighted_euclidean(pred, target, R2, mask):
    """R2-WEIGHTED Euclidean distance, NOT averaged by the weights: sum over
    vertices divided by N (not by sum of weights). The 'weighted but not
    averaged' counterpart of loss_euclidean (which divides by Σ R2). Retains more
    individual variability at matched accuracy (Stage 6) -- the visualCoord
    default. With fixed graph size /N is constant, so this is the R2-weighted SUM
    up to a constant; per-batch scale floats with total R2 mass (grad-clip keeps
    it stable)."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    w = R2 * mask.float()
    return (w * dist).sum() / dist.numel()


# --loss options for visualCoord. 'weighted_euclidean' is the default (see
# train.py); 'euclidean' (the R2-weighted average) is kept as the comparison
# baseline. (Stage-1-3 explored mse / smoothl1 / ecc_weighted / ecc_balanced --
# all rejected; see the archived plan + QRIS provenance.)
LOSSES = {
    'euclidean': loss_euclidean,
    'weighted_euclidean': loss_weighted_euclidean,
}


# ---- pRF-size (single-output) loss ----------------------------------------
# The visualCoord losses above take (N, 2) coordinates; this takes the (N,)
# scalar pRF-size prediction/target. Stage 5 compared 'legacy' vs a normalized
# variant and 'legacy' won (better error + more individual variability), so it is
# the only kept / default pRFsize loss.

def prf_legacy(pred, target, R2, mask):
    """Original toolbox pRF-size loss: Smooth-L1 on R2-scaled pred & target,
    plain mean over all vertices (un-normalized)."""
    return F.smooth_l1_loss(R2 * pred, R2 * target)


PRF_LOSSES = {
    'legacy': prf_legacy,
}
