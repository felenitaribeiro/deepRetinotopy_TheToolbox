"""Loss functions for the visualCoord (joint Cartesian visual-field) model.

Each loss takes (pred, target, R2, mask) where pred/target are (N, 2) normalized
Cartesian coordinates, R2 is the per-vertex variance explained (used as a
weight), and mask is the per-vertex validity boolean. All are R2-weighted means
over valid vertices; they differ in how they weight across the visual field.

LOSSES maps the --loss CLI name to the function (used by main/train.py).
"""
import torch
import torch.nn.functional as F

EPS = 1e-8


def _weighted_mean(per_vertex, weight):
    return (weight * per_vertex).sum() / (weight.sum() + EPS)


def loss_euclidean(pred, target, R2, mask):
    """R2-weighted mean Euclidean distance in Cartesian visual-field space."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    return _weighted_mean(dist, R2 * mask.float())


def loss_mse(pred, target, R2, mask):
    """R2-weighted mean squared error on (x, y). Up-weights large (peripheral)
    errors relative to the plain distance."""
    se = ((pred - target) ** 2).sum(dim=1)
    return _weighted_mean(se, R2 * mask.float())


def loss_smoothl1(pred, target, R2, mask):
    """R2-weighted Smooth-L1 (Huber) on the 2D residual; robust to outliers."""
    per = F.smooth_l1_loss(pred, target, reduction='none').sum(dim=1)
    return _weighted_mean(per, R2 * mask.float())


def loss_ecc_weighted(pred, target, R2, mask):
    """R2-weighted Euclidean distance, additionally weighted by empirical
    eccentricity (normalized radius) to push the model to fit the periphery."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    r_emp = torch.sqrt((target ** 2).sum(dim=1) + 1e-12)  # normalized ecc in [0, 1]
    return _weighted_mean(dist, R2 * mask.float() * r_emp)


def loss_ecc_balanced(pred, target, R2, mask, n_bands=8):
    """R2-weighted Euclidean distance, re-weighted so each eccentricity band
    contributes EQUALLY (neutralizes cortical magnification: the fovea is
    over-represented on the cortical surface). Unlike ecc_weighted this does not
    tilt toward the periphery -- it just removes the vertex-density imbalance.
    weight = R2*mask / (R2-weighted mass in that vertex's eccentricity band)."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    r = torch.sqrt((target ** 2).sum(dim=1) + 1e-12)            # normalized ecc in [0, 1]
    w = R2 * mask.float()
    band = torch.clamp((r * n_bands).long(), 0, n_bands - 1)
    band_mass = torch.zeros(n_bands, device=pred.device, dtype=w.dtype).scatter_add_(0, band, w)
    return _weighted_mean(dist, w / (band_mass[band] + EPS))


LOSSES = {
    'euclidean': loss_euclidean,
    'mse': loss_mse,
    'smoothl1': loss_smoothl1,
    'ecc_weighted': loss_ecc_weighted,
    'ecc_balanced': loss_ecc_balanced,
}
