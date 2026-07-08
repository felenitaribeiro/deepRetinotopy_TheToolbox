#!/usr/bin/env python3
"""Render the deepretinotopy neurocontainers recipe from the manifest + template.

The published recipe (neurodesk/neurocontainers recipes/deepretinotopy/build.yaml)
only differs from release to release in four spots: the version, the pinned commit,
the list of model weights to fetch, and the CPU-version note in the readme. This
script fills those into container/build.yaml.tmpl from container/manifest.yaml and
the current git tag/commit, so the recipe is generated rather than hand-edited.

Usage:
    python container/render_recipe.py                       # infer version/commit from git
    python container/render_recipe.py --version 1.0.19 --commit <sha>
    python container/render_recipe.py -o /tmp/build.yaml    # write somewhere else

With no --output, the rendered recipe is printed to stdout.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "manifest.yaml"
DEFAULT_TEMPLATE = HERE / "build.yaml.tmpl"

# Fixed emission order for the model download loop (matches the published recipe).
HEMIS = ("LH", "RH")
MAPS = ("polarAngle", "eccentricity", "pRFsize")


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=HERE, text=True).strip()


def latest_tag() -> str:
    """Most recent tag reachable from HEAD (e.g. 'v1.0.6')."""
    return _git("describe", "--tags", "--abbrev=0")


def commit_for_ref(ref: str) -> str:
    """Full commit SHA that a ref (tag/branch/HEAD) points to."""
    return _git("rev-list", "-n", "1", ref)


def build_model_files(manifest: dict) -> str:
    prefix = manifest["osf_model_dir"].rstrip("/")
    models = manifest["models"]
    files = []
    for hemi in HEMIS:
        for m in MAPS:
            seed = models[hemi][m]
            files.append(f"{prefix}/deepRetinotopy_{m}_{hemi}_model{seed}.pt")
    return " ".join(files)


def render(version: str, commit: str, manifest_path: Path, template_path: Path) -> str:
    manifest = yaml.safe_load(manifest_path.read_text())
    template = template_path.read_text()

    substitutions = {
        "@@VERSION@@": version,
        "@@COMMIT@@": commit,
        "@@MODEL_FILES@@": build_model_files(manifest),
    }
    out = template
    for token, value in substitutions.items():
        if token not in out:
            raise SystemExit(f"error: token {token} missing from template {template_path}")
        out = out.replace(token, value)

    if "@@" in out:
        raise SystemExit("error: unresolved @@...@@ token remains in rendered recipe")

    # Sanity check: the result must be valid YAML.
    yaml.safe_load(out)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", help="Version string (default: latest git tag, leading 'v' stripped).")
    p.add_argument("--commit", help="Commit SHA to pin (default: the commit the version tag points to).")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    p.add_argument("-o", "--output", type=Path, help="Write here instead of stdout.")
    args = p.parse_args(argv)

    version = args.version
    commit = args.commit
    if version is None or commit is None:
        tag = latest_tag()
        if version is None:
            version = tag[1:] if tag.startswith("v") else tag
        if commit is None:
            commit = commit_for_ref(tag)

    recipe = render(version, commit, args.manifest, args.template)

    if args.output:
        args.output.write_text(recipe)
        print(f"wrote {args.output} (version={version}, commit={commit})", file=sys.stderr)
    else:
        sys.stdout.write(recipe)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
