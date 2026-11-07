"""Compute Cosine Similarity and BERTScore (F1) for all QA pairs and compute average scores.

Usage:
    python scripts/compute_evaluation_metrics.py
"""
import math
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Set matplotlib temp cache to avoid warning
os.environ["MPLCONFIGDIR"] = str(Path(__file__).resolve().parents[1] / "outputs" / ".mplcache")

ONEDRIVE_FILE = Path(r"C:\Users\Vishesh G Devanur\OneDrive\Documents\student_testing_log.csv.xlsx")
PROJECT_FILE = Path(r"D:\ENILS\enils\outputs\student_testing_log.xlsx")
EVAL_FILE = Path(r"C:\Users\Vishesh G Devanur\OneDrive\Documents\student_testing_log_evaluation.xlsx")
COMPANION_FILE = Path(r"C:\Users\Vishesh G Devanur\OneDrive\Documents\student_testing_log_with_cosine.xlsx")

HEADERS = [
    "Timestamp",
    "Question Asked",
    "Tutor Output",
    "Expected Answer",
    "Cosine Similarity (%)",
    "BERTScore (F1 %)",
    "RAG Knowledge Source",
    "Latency (s)",
    "Review / Notes",
]

def text_to_vector(text: str) -> Counter:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return Counter(words)

def compute_cosine(t1: str, t2: str) -> float:
    if not t1 or not t2:
        return 0.0
    v1 = text_to_vector(t1)
    v2 = text_to_vector(t2)
    intersection = set(v1.keys()) & set(v2.keys())
    numerator = sum([v1[x] * v2[x] for x in intersection])
    sum1 = sum([v1[x]**2 for x in v1.keys()])
    sum2 = sum([v2[x]**2 for x in v2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    return float(numerator) / denominator

def main():
    # Check source file: prefer temp_user_log.xlsx or student_testing_log.xlsx in project
    source_path = PROJECT_FILE
    if (PROJECT_FILE.parent / "temp_user_log.xlsx").exists():
        source_path = PROJECT_FILE.parent / "temp_user_log.xlsx"
    elif ONEDRIVE_FILE.exists():
        try:
            temp_copy = PROJECT_FILE.parent / "temp_eval_read.xlsx"
            subprocess.run(
                f'powershell -Command "Copy-Item -Path \'{ONEDRIVE_FILE}\' -Destination \'{temp_copy}\' -Force"',
                shell=True
            )
            if temp_copy.exists():
                source_path = temp_copy
        except Exception:
            pass

    wb_in = openpyxl.load_workbook(source_path)
    ws_in = wb_in.active

    # Collect rows
    rows_data = []
    cands = []
    refs = []
    eval_indices = []

    for r in range(2, ws_in.max_row + 1):
        vals = [cell.value for cell in ws_in[r]]
        if not any(vals):
            continue
        timestamp = vals[0] if len(vals) > 0 and vals[0] else ""
        question = str(vals[1]).strip() if len(vals) > 1 and vals[1] else ""
        tutor_out = str(vals[2]).strip() if len(vals) > 2 and vals[2] else ""
        expected = str(vals[3]).strip() if len(vals) > 3 and vals[3] else ""
        rag_src = str(vals[4]).strip() if len(vals) > 4 and vals[4] else ""
        latency = vals[5] if len(vals) > 5 and vals[5] is not None else ""
        notes = str(vals[6]).strip() if len(vals) > 6 and vals[6] else ""

        if not question and not tutor_out:
            continue

        row_idx = len(rows_data)
        rows_data.append({
            "timestamp": timestamp,
            "question": question,
            "tutor_out": tutor_out,
            "expected": expected,
            "rag_src": rag_src,
            "latency": latency,
            "notes": notes,
            "cosine": None,
            "bert_f1": None
        })

        if tutor_out and expected:
            cands.append(tutor_out)
            refs.append(expected)
            eval_indices.append(row_idx)

    # Compute Cosine Similarity
    for r in rows_data:
        if r["tutor_out"] and r["expected"]:
            r["cosine"] = compute_cosine(r["tutor_out"], r["expected"])

    # Compute BERTScore using distilbert
    print(f"Calculating BERTScore for {len(cands)} pairs...")
    if cands:
        import bert_score
        P, R, F1 = bert_score.score(cands, refs, model_type="distilbert-base-uncased", verbose=False)
        for i, row_idx in enumerate(eval_indices):
            rows_data[row_idx]["bert_f1"] = F1[i].item()

    # Create new workbook
    wb_out = openpyxl.Workbook()
    ws_out = wb_out.active
    ws_out.title = "Student Evaluation & Metrics"

    # Header row (clean, plain - no fill colors)
    ws_out.append(HEADERS)
    header_font = Font(name="Calibri", size=11, bold=True)
    for cell in ws_out[1]:
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws_out.row_dimensions[1].height = 24

    font_normal = Font(name="Calibri", size=11)

    cos_scores = []
    bert_scores = []
    latencies = []

    for r in rows_data:
        cos_str = f"{r['cosine']*100:.1f}%" if r["cosine"] is not None else ""
        bert_str = f"{r['bert_f1']*100:.1f}%" if r["bert_f1"] is not None else ""
        lat_val = r["latency"]
        lat_str = f"{float(lat_val):.2f}" if (lat_val != "" and lat_val is not None) else ""

        if r["cosine"] is not None:
            cos_scores.append(r["cosine"])
        if r["bert_f1"] is not None:
            bert_scores.append(r["bert_f1"])
        if lat_val != "" and lat_val is not None:
            try:
                latencies.append(float(lat_val))
            except ValueError:
                pass

        row_vals = [
            r["timestamp"],
            r["question"],
            r["tutor_out"],
            r["expected"],
            cos_str,
            bert_str,
            r["rag_src"],
            lat_str,
            r["notes"]
        ]
        ws_out.append(row_vals)
        cur_row = ws_out.max_row
        ws_out.row_dimensions[cur_row].height = 20

        for col_idx, cell in enumerate(ws_out[cur_row], start=1):
            cell.font = font_normal
            if col_idx in (2, 3, 4):  # Question, Tutor, Expected
                cell.alignment = Alignment(vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

    # Add Blank Separator Row
    ws_out.append([""] * len(HEADERS))

    # Add Average Summary Row (Plain, no background color)
    avg_cos = (sum(cos_scores) / len(cos_scores)) * 100 if cos_scores else 0.0
    avg_bert = (sum(bert_scores) / len(bert_scores)) * 100 if bert_scores else 0.0
    avg_lat = (sum(latencies) / len(latencies)) if latencies else 0.0

    summary_row = [
        "AVERAGE / SUMMARY",
        f"Evaluated on {len(eval_indices)} question-answer pairs",
        "",
        "AVERAGE SCORES:",
        f"{avg_cos:.2f}%",
        f"{avg_bert:.2f}%",
        "RAG Chapter 1 Grounded",
        f"{avg_lat:.2f}s",
        "Benchmark Complete"
    ]
    ws_out.append(summary_row)
    sum_row_idx = ws_out.max_row
    ws_out.row_dimensions[sum_row_idx].height = 24

    sum_font = Font(name="Calibri", size=11, bold=True)
    for col_idx, cell in enumerate(ws_out[sum_row_idx], start=1):
        cell.font = sum_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Column widths
    col_widths = {
        1: 20,  # Timestamp
        2: 35,  # Question Asked
        3: 50,  # Tutor Output
        4: 45,  # Expected Answer
        5: 22,  # Cosine Similarity (%)
        6: 22,  # BERTScore (F1 %)
        7: 35,  # RAG Knowledge Source
        8: 15,  # Latency (s)
        9: 25,  # Review / Notes
    }
    for col_idx, width in col_widths.items():
        ws_out.column_dimensions[get_column_letter(col_idx)].width = width

    # Save to clean project file and try all other locations
    clean_project_file = PROJECT_FILE.parent / "student_testing_log_clean.xlsx"
    clean_onedrive_file = ONEDRIVE_FILE.parent / "student_testing_log_clean.xlsx"
    wb_out.save(clean_project_file)
    print(f"[OK] Saved clean plain version to: {clean_project_file}")

    for dest in [clean_onedrive_file, PROJECT_FILE, EVAL_FILE, COMPANION_FILE, ONEDRIVE_FILE]:
        try:
            wb_out.save(dest)
            print(f"[OK] Saved to: {dest}")
        except PermissionError:
            print(f"[Notice] {dest.name} is currently open in Excel. Close it to update directly.")
        except Exception:
            pass

    print("\n" + "="*60)
    print("EVALUATION BENCHMARK SUMMARY:")
    print(f"Total Evaluated Questions: {len(eval_indices)}")
    print(f"Average Cosine Similarity:  {avg_cos:.2f}%  (Lexical / Word Overlap)")
    print(f"Average BERTScore (F1):    {avg_bert:.2f}%  (Deep Semantic Similarity)")
    print(f"Average Perceived Latency: {avg_lat:.2f} seconds")
    print("="*60)

if __name__ == "__main__":
    main()
