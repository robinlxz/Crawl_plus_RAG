import argparse
import json
import os
import sys
from pathlib import Path
from statistics import mean

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from retrieval.search_engine import SimpleRAGSearcher


def load_cases(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def match_targets(result, targets):
    title = result.get("source_meta", {}).get("title", "") or ""
    url = result.get("source_meta", {}).get("url", "") or ""
    for t in targets:
        tc = t.get("title_contains")
        uc = t.get("url_contains")
        if tc and tc.lower() in title.lower():
            return True
        if uc and uc.lower() in url.lower():
            return True
    return False


def eval_query(searcher, query, targets, ks):
    metrics = {}
    results_full = searcher.search(query, top_k=max(ks))
    for k in ks:
        results = results_full[:k]
        covered = any(match_targets(r, targets) for r in results)
        mrr = 0.0
        for i, r in enumerate(results, 1):
            if match_targets(r, targets):
                mrr = 1.0 / i
                break
        top1_scores = [results[0]["score"]] if results else []
        top3_scores = [r["score"] for r in results[:3]]
        metrics[f"Coverage@{k}"] = 1.0 if covered else 0.0
        metrics[f"MRR@{k}"] = mrr
        metrics[f"Top1AvgScore@{k}"] = mean(top1_scores) if top1_scores else 0.0
        metrics[f"Top3AvgScore@{k}"] = mean(top3_scores) if top3_scores else 0.0
    return metrics, results_full


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases_path", default=str(Path(current_dir).parent.parent / "data" / "eval" / "ecs_bilingual_eval.json"))
    parser.add_argument("--index_path", default=str(Path(current_dir).parent.parent / "data" / "byteplus.index"))
    parser.add_argument("--meta_path", default=str(Path(current_dir).parent.parent / "data" / "byteplus_meta.json"))
    parser.add_argument("--output_json", default=str(Path(current_dir).parent.parent / "data" / "eval" / "results_bilingual_eval.json"))
    parser.add_argument("--output_md", default=str(Path(current_dir).parent.parent / "data" / "eval" / "results_bilingual_eval.md"))
    args = parser.parse_args()

    ks = [3, 5, 10]
    searcher = SimpleRAGSearcher(index_path=args.index_path, meta_path=args.meta_path)
    cases = load_cases(args.cases_path)

    results = []
    for case in cases:
        rid = case["id"]
        zh = case["zh_query"]
        en = case["en_query"]
        targets = case["targets"]
        zh_metrics, _ = eval_query(searcher, zh, targets, ks)
        en_metrics, _ = eval_query(searcher, en, targets, ks)
        results.append({
            "id": rid,
            "zh_query": zh,
            "en_query": en,
            "zh_metrics": zh_metrics,
            "en_metrics": en_metrics
        })

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    lines = []
    lines.append("# Bilingual Evaluation Results")
    lines.append("")
    lines.append("|ID|Query(ZH)|Coverage@3(ZH)|MRR@3(ZH)|Top1@3(ZH)|Coverage@3(EN)|MRR@3(EN)|Top1@3(EN)|")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")
    for r in results:
        zh_cov3 = r["zh_metrics"]["Coverage@3"]
        zh_mrr3 = r["zh_metrics"]["MRR@3"]
        zh_t1_3 = r["zh_metrics"]["Top1AvgScore@3"]
        en_cov3 = r["en_metrics"]["Coverage@3"]
        en_mrr3 = r["en_metrics"]["MRR@3"]
        en_t1_3 = r["en_metrics"]["Top1AvgScore@3"]
        lines.append(f"|{r['id']}|{r['zh_query']}|{zh_cov3:.2f}|{zh_mrr3:.3f}|{zh_t1_3:.4f}|{en_cov3:.2f}|{en_mrr3:.3f}|{en_t1_3:.4f}|")
    lines.append("")
    lines.append("See JSON for full metrics including @5/@10 and Top3 averages.")

    Path(os.path.dirname(args.output_md)).mkdir(parents=True, exist_ok=True)
    with open(args.output_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()

