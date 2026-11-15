"""Load config.yaml, validate it, and resolve paths relative to the project root."""

from __future__ import annotations

from pathlib import Path

import yaml

from .validation import ClutchIQError, validate_config

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path | None = None) -> dict:
    cfg_path = Path(path) if path else ROOT / "config.yaml"
    if not cfg_path.exists():
        raise ClutchIQError(f"Settings file not found: {cfg_path}")
    try:
        with open(cfg_path, encoding="utf-8") as fh:
            cfg = yaml.safe_load(fh)
    except yaml.YAMLError as e:
        raise ClutchIQError(f"{cfg_path.name} is not valid YAML: {e}") from e
    validate_config(cfg)

    raw = None
    for cand in cfg["paths"]["raw_dirs"]:
        p = (ROOT / cand).resolve()
        if (p / "ball_by_ball.csv").exists():
            raw = p
            break
    if raw is None:
        tried = ", ".join(str((ROOT / c).resolve()) for c in cfg["paths"]["raw_dirs"])
        raise ClutchIQError(
            "Could not find ball_by_ball.csv. Put the 6 Data Pack CSVs in data/raw/, keep this folder next to "
            f"'CLUTCHIQ DATASET', or edit paths.raw_dirs in config.yaml. Looked in: {tried}"
        )
    cfg["paths"]["raw"] = raw
    for k in ("processed_dir", "outputs_dir", "figures_dir"):
        p = ROOT / cfg["paths"][k]
        p.mkdir(parents=True, exist_ok=True)
        cfg["paths"][k] = p
    a = cfg.get("auction")
    if a:
        for k in ("status_file", "rr_squad_file", "reports_file"):
            if a.get(k):
                a[k] = (ROOT / a[k]).resolve()
    return cfg
