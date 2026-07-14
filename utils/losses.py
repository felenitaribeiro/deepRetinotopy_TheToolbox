"""Loss functions for training.

Two objectives, selected by prediction type in main/train.py:
  - visualCoord (N, 2 Cartesian coordinates)          -> loss_weighted_euclidean
  - single-output maps (pRFsize / polarAngle / eccentricity, N,) -> loss_legacy

Both take (pred, target, R2, mask): R2 is the per-vertex variance explained (used
as a weight) and mask is the per-vertex validity boolean.
"""
import torch
import torch.nn.functional as F


def loss_weighted_euclidean(pred, target, R2, mask):
    """R2-weighted Euclidean distance in Cartesian visual-field space, summed over
    vertices and divided by N (weighted, NOT averaged by Σ R2). Used for the
    visualCoord model. Its per-batch scale floats with total R2 mass --
    grad-clip keeps it stable."""
    dist = torch.sqrt(((pred - target) ** 2).sum(dim=1) + 1e-12)
    w = R2 * mask.float()
    return (w * dist).sum() / dist.numel()


def loss_legacy(pred, target, R2, mask):
    """Legacy single-map loss (polarAngle / eccentricity / pRFsize): Smooth-L1 on
    R2-scaled prediction & target, mean over all vertices. Matches the original
    toolbox behaviour."""
    return F.smooth_l1_loss(R2 * pred, R2 * target)
