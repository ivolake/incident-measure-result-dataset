from __future__ import annotations

import argparse
from pathlib import Path

from .io import write_json, write_jsonl
from .metrics import evaluate_predictions
from .rankers import rank_bm25, rank_embeddings
from .validation import validate_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="incident-measure-result")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate dataset structure")
    validate.add_argument("--dataset", default="data/external_gold_seed_8_8_35")
    validate.add_argument("--annotations", default="data/annotations/subagent_annotations")
    validate.add_argument("--out")

    bm25 = subparsers.add_parser("rank-bm25", help="Run dependency-free BM25 ranking")
    bm25.add_argument("--dataset", default="data/external_gold_seed_8_8_35")
    bm25.add_argument("--top-k", type=int, default=5)
    bm25.add_argument("--out", required=True)

    embeddings = subparsers.add_parser("rank-embeddings", help="Run SentenceTransformers embedding ranking")
    embeddings.add_argument("--dataset", default="data/external_gold_seed_8_8_35")
    embeddings.add_argument("--model", required=True)
    embeddings.add_argument("--top-k", type=int, default=5)
    embeddings.add_argument("--batch-size", type=int, default=32)
    embeddings.add_argument("--out", required=True)

    evaluate = subparsers.add_parser("evaluate", help="Evaluate top-k predictions")
    evaluate.add_argument("--dataset", default="data/external_gold_seed_8_8_35")
    evaluate.add_argument("--predictions", required=True)
    evaluate.add_argument("--out")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "validate":
        report = validate_dataset(args.dataset, args.annotations)
        if args.out:
            write_json(args.out, report)
        else:
            print(report)
    elif args.command == "rank-bm25":
        rows = rank_bm25(args.dataset, top_k=args.top_k)
        write_jsonl(args.out, rows)
    elif args.command == "rank-embeddings":
        rows = rank_embeddings(args.dataset, args.model, top_k=args.top_k, batch_size=args.batch_size)
        write_jsonl(args.out, rows)
    elif args.command == "evaluate":
        report = evaluate_predictions(args.dataset, args.predictions)
        if args.out:
            write_json(args.out, report)
        else:
            print(report)
    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
