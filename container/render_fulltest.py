#!/usr/bin/env python3
"""Render the deepretinotopy neurocontainers test suite from manifest + template.

Companion to render_recipe.py. The published test suite
(neurodesk/neurocontainers recipes/deepretinotopy/fulltest.yaml) only differs
from release to release in two spots: the version and the set of model .pt
files the "model tests" look for. This script fills those into
container/fulltest.yaml.tmpl from container/manifest.yaml, so the model tests
stay in sync with what build.yaml actually ships -- the same manifest drives
both the recipe and its test suite.

The container line follows the neurocontainers convention (see recipes/civet):
`container: deepretinotopy_${version}_REFERENCE.simg`, where `${version}` and
`REFERENCE` are resolved by the test harness against the build under test -- no
build date is baked in.

Usage:
    python container/render_fulltest.py                       # infer version from git tag
    python container/render_fulltest.py --version 1.0.19
    python container/render_fulltest.py -o /tmp/fulltest.yaml # write somewhere else

With no --output, the rendered suite is printed to stdout.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

# Reuse the canonical hemisphere/map ordering and the git helper from the
# recipe renderer so the two never drift. Both scripts live in this directory,
# which Python puts on sys.path[0] when either is run as a script.
from render_recipe import HEMIS, MAPS, latest_tag

HERE = Path(__file__).resolve().parent
DEFAULT_MANIFEST = HERE / "manifest.yaml"
DEFAULT_TEMPLATE = HERE / "fulltest.yaml.tmpl"

MODELS_DIR = "/opt/deepRetinotopy_TheToolbox/models"

# Human-facing name + description for each map's "models exist" test. A map in
# the manifest but not here still renders, with a generic label.
MAP_TESTS = {
    "visualCoord": (
        "Visual field coordinate models exist",
        "Verify visual field coordinate (polar angle + eccentricity) prediction models are installed",
    ),
    "pRFsize": (
        "pRF size models exist",
        "Verify pRF size prediction models are installed",
    ),
}


def _load_model_command(path: str) -> str:
    """The `command` string (post-YAML-parse) for the load-a-model test.

    Mirrors the published suite verbatim; only the model file path differs.
    yaml.dump re-escapes this for us, so we just build the raw shell string.
    """
    q = "'\"'\"'"  # the classic bash single-quote-inside-single-quote escape
    return (
        f"bash -lc 'python -c \"import torch; "
        f"m=torch.load({q}{path}{q}, "
        f"map_location={q}cpu{q}, weights_only=False); "
        f"print({q}Model loaded successfully{q})\"'"
    )


def build_model_tests(manifest: dict) -> str:
    """Render the DEEPRETINOTOPY MODEL TESTS block from the manifest models.

    Emits one "models exist" test per map (in MAPS order), a file-count test,
    and a load-a-model test -- all derived from the actual shipped weights, so
    they track build.yaml's model list instead of the stale 6-model scheme.
    """
    manifest_maps = {m for hemi in manifest["models"].values() for m in hemi}
    maps = [m for m in MAPS if m in manifest_maps]
    unknown = manifest_maps - set(MAPS)
    if unknown:
        raise SystemExit(f"error: manifest has maps not in MAPS ordering: {sorted(unknown)}")

    tests: list[dict] = []
    for m in maps:
        name, desc = MAP_TESTS.get(
            m, (f"{m} models exist", f"Verify {m} prediction models are installed")
        )
        tests.append(
            {
                "name": name,
                "description": desc,
                "command": f"bash -lc 'ls -la {MODELS_DIR}/deepRetinotopy_{m}_*.pt'",
                "expected_output_contains": f"deepRetinotopy_{m}_LH_model.pt",
            }
        )

    count = len(maps) * len(HEMIS)
    tests.append(
        {
            "name": "Model file count",
            "description": f"Verify all {count} model files are present (LH/RH for {len(maps)} maps)",
            "command": f"bash -lc 'ls {MODELS_DIR}/*.pt | wc -l'",
            "expected_output_contains": str(count),
        }
    )

    first = f"{MODELS_DIR}/deepRetinotopy_{maps[0]}_{HEMIS[0]}_model.pt"
    tests.append(
        {
            "name": "Load PyTorch model",
            "description": "Test loading a deepRetinotopy model file",
            "command": _load_model_command(first),
            "expected_output_contains": "Model loaded successfully",
        }
    )

    dumped = yaml.dump(
        tests, sort_keys=False, default_flow_style=False, width=10**9, allow_unicode=True
    )
    # Indent two spaces so the list sits under `tests:` like the hand-written items.
    return "\n".join(("  " + line if line else line) for line in dumped.rstrip("\n").split("\n"))


def render(version: str, manifest_path: Path, template_path: Path) -> str:
    manifest = yaml.safe_load(manifest_path.read_text())
    template = template_path.read_text()

    substitutions = {
        "@@VERSION@@": version,
        "@@MODEL_TESTS@@": build_model_tests(manifest),
    }
    out = template
    for token, value in substitutions.items():
        if token not in out:
            raise SystemExit(f"error: token {token} missing from template {template_path}")
        out = out.replace(token, value)

    if "@@" in out:
        raise SystemExit("error: unresolved @@...@@ token remains in rendered fulltest")

    # Sanity check: the result must be valid YAML. (${version}/REFERENCE are
    # plain scalars resolved later by the harness -- fine to parse here.)
    yaml.safe_load(out)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--version", help="Version string (default: latest git tag, leading 'v' stripped).")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    p.add_argument("-o", "--output", type=Path, help="Write here instead of stdout.")
    args = p.parse_args(argv)

    version = args.version
    if version is None:
        tag = latest_tag()
        version = tag[1:] if tag.startswith("v") else tag

    suite = render(version, args.manifest, args.template)

    if args.output:
        args.output.write_text(suite)
        print(f"wrote {args.output} (version={version})", file=sys.stderr)
    else:
        sys.stdout.write(suite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
