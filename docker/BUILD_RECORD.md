# Image build record

| Tag | Built | Host | Source | Size | Image ID |
|---|---|---|---|---|---|
| `cal-disp:0.3.0-rc` | 2026-10-05 | aurora (`docker/build-docker-image.sh`, `--network=host`) | `gamma-release` `7085ec9`, version `0.2.post1.dev79+g7085ec96e` | 1.5 GB | `sha256:fc115560ebf97907c112d7096a7fb7796506e794122a3c8e369c87d969691333` |

Key versions inside: Python 3.13.15, GDAL 3.13.3, PROJ 9.8.1, rasterio 1.5.1,
numpy 2.5.3, scipy 1.18.1, opera-utils 0.25.8, venti `2a7e61f`. Full conda
list: `installed_packages_0.3.0rc.csv` (214 packages).

## Validation inside the image

```bash
docker run --rm --user $(id -u):$(id -g) -e NUMPY_MADVISE_HUGEPAGE=0 -e HOME=/tmp \
  -v $PWD:/home/work -w /home/work cal-disp:0.3.0-rc \
  bash -lc 'eval "$(micromamba shell hook --shell bash)" && micromamba activate cal-disp \
            && scripts/run_validation.sh --golden-dir test_golden'
```

2026-10-05: **passed at 1e-6** against the golden built on aurora with the
pixi `dev` env (GDAL 3.11 line); peak memory 6.31 GB. The golden is therefore
reproducible across the two environments for the gamma configuration.
