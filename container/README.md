# Container recipe automation

This directory generates the [Neurodesk](https://www.neurodesk.org/) build recipe
for deepretinotopy so it no longer has to be hand-edited in
[neurodesk/neurocontainers](https://github.com/neurodesk/neurocontainers/blob/main/recipes/deepretinotopy/build.yaml).

| File | Role |
|------|------|
| `manifest.yaml` | **Source of truth.** Model-seed selection per map/hemisphere and the OSF project. |
| `build.yaml.tmpl` | The recipe with three holes (`@@VERSION@@`, `@@COMMIT@@`, `@@MODEL_FILES@@`). |
| `render_recipe.py` | Fills the template from the manifest + git tag/commit and prints/writes `build.yaml`. |

The published `recipes/deepretinotopy/build.yaml` is a **generated artifact** — never
edit it by hand. Change the manifest (or, for structural changes, the template) and
re-render.

## Cutting a release

1. Update `manifest.yaml` if the shipped model seeds changed (usually the only edit).
2. Tag the release: `git tag v1.0.19 && git push --tags`.
3. The [`publish neurocontainer recipe`](../.github/workflows/publish_recipe.yml)
   workflow renders the recipe and opens a PR to neurocontainers from your fork.
4. Review the PR diff (version, commit, changed seeds) and merge upstream.

`version` comes from the tag; the pinned `commit` is the tagged commit — both are
injected by the workflow, not stored in the manifest.

## Rendering locally

```bash
pip install pyyaml
python container/render_recipe.py                         # uses the latest git tag
python container/render_recipe.py --version 1.0.19 --commit <sha> -o build.yaml
```

The renderer validates that no `@@token@@` is left unresolved and that the output
parses as YAML.

Up to 1.0.18 the template reproduced the published recipe byte-for-byte:

```bash
python container/render_recipe.py --version 1.0.18 \
  --commit fd8382bfa168727feb53946fdab4fe838908e5f2
```

That no longer holds — the template intentionally diverges from the published
1.0.18 recipe in two places (see the comments in `build.yaml.tmpl`):

- `pyg_lib` and `torch_sparse` are no longer installed. Their `pt25cu124` wheels
  require GLIBC_2.29+, which the CentOS 8 base image (glibc 2.28) does not
  provide, so they never loaded at runtime.
- The final cleanup step targets `/opt/miniconda-latest/...` rather than
  `/opt/miniconda/...`, which does not exist and made those `rm -rf` calls no-ops.

## One-time CI setup

The workflow opens a cross-repo PR, which needs credentials the default
`GITHUB_TOKEN` can't provide:

1. Fork `neurodesk/neurocontainers` to `felenitaribeiro/neurocontainers` (if not
   already). The `FORK`/`UPSTREAM` names are set at the top of the workflow.
2. Create a Personal Access Token with write access to your fork
   (fine-grained: *Contents* + *Pull requests* read/write; or a classic `repo` token).
3. Add it as the repository secret **`NEUROCONTAINERS_PAT`**
   (Settings → Secrets and variables → Actions).

Run the workflow manually with **dry_run: true** first to render and inspect the
recipe without opening a PR.