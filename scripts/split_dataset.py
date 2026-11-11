import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.data.scan import scan_dataset
from src.data.split import (
    DEFAULT_RATIOS,
    build_stratified_splits,
    check_disjoint,
    remove_duplicate_copies,
    split_summary,
    write_splits,
)


def _ratios_from_args(args):
    ratios = {"train": args.train, "val": args.val, "test": args.test}
    if abs(sum(ratios.values()) - 1.0) > 1e-6:
        raise SystemExit(f"split ratios must sum to 1.0, got {sum(ratios.values())}")
    return ratios


def main():
    parser = argparse.ArgumentParser(
        description="Create stratified 70/15/15 splits for a PlantVillage-style dataset."
    )
    parser.add_argument("--data-root", default="data/plantvillage")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out-dir", default="splits")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--train", type=float, default=DEFAULT_RATIOS["train"])
    parser.add_argument("--val", type=float, default=DEFAULT_RATIOS["val"])
    parser.add_argument("--test", type=float, default=DEFAULT_RATIOS["test"])
    parser.add_argument("--json", dest="json_path", default="results/data_scan.json")
    parser.add_argument(
        "--no-dedupe",
        action="store_true",
        help="Do not drop exact duplicate copies before splitting.",
    )
    args = parser.parse_args()

    ratios = _ratios_from_args(args)
    project_root = Path(args.project_root).resolve()
    data_root = Path(args.data_root)
    if not data_root.is_absolute():
        data_root = project_root / data_root
    if not data_root.is_dir():
        print(f"[ERROR] data root not found: {data_root}")
        return 1

    report = scan_dataset(
        data_root,
        project_root=project_root,
        hash_duplicates=not args.no_dedupe,
        include_images=True,
    )
    items = report["images"]
    if not items:
        print("[ERROR] no valid images found, nothing to split.")
        return 1

    kept = items
    if not args.no_dedupe and report["duplicates"]:
        kept, removed = remove_duplicate_copies(items, report["duplicates"])
        print(f"dropped duplicate copies: {len(removed)}")
    if report["cross_class_duplicates"]:
        print(
            "[WARNING] identical images found under different classes: "
            f"{len(report['cross_class_duplicates'])} group(s); not auto-dropped, "
            "please audit labels before final training."
        )

    splits = build_stratified_splits(kept, seed=args.seed, ratios=ratios)
    check_disjoint(splits)

    class_names = sorted({item["class_name"] for item in kept})
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = project_root / out_dir
    class_to_idx = write_splits(splits, out_dir, class_names)

    summary = split_summary(splits)
    print(f"classes: {len(class_names)}, usable images: {summary['total']}")
    for split_name in ("train", "val", "test"):
        info = summary[split_name]
        print(
            f"  {split_name}: {info['count']} ({info['ratio'] * 100:.1f}%)"
        )
    print(f"class_to_idx written to {out_dir / 'class_to_idx.json'}")

    if report["damaged"]:
        print(f"excluded damaged images: {len(report['damaged'])}")

    json_path = Path(args.json_path)
    if not json_path.is_absolute():
        json_path = project_root / json_path
    json_path.parent.mkdir(parents=True, exist_ok=True)
    scan_summary = {k: v for k, v in report.items() if k != "images"}
    json_path.write_text(
        json.dumps(scan_summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"scan report written to {json_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
