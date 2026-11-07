"""Automatic Excel and CSV session logger for student voice interactions.

Saves each question and answer turn in real-time to:
  outputs/student_testing_log.xlsx
and a CSV backup:
  outputs/student_testing_log.csv

Handles file permissions gracefully (e.g. if the user has the file open in Excel).
Includes Cosine Similarity calculation between Tutor Output and Expected Answer.
"""
import csv
import datetime
import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Optional

try:
    import openpyxl
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

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


def log_turn(
    output_dir: Path,
    question: str,
    tutor_reply: str,
    rag_sources: Optional[List[str]] = None,
    latency_s: Optional[float] = None,
    expected_answer: str = "",
    notes: str = "",
):
    """Safely append a question and answer turn to Excel and CSV."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    xlsx_path = output_dir / "student_testing_log.xlsx"
    csv_path = output_dir / "student_testing_log.csv"

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources_str = ", ".join(rag_sources) if rag_sources else "N/A"
    lat_str = f"{latency_s:.2f}" if latency_s is not None else ""

    sim_val = None
    sim_str = ""
    bert_str = ""
    if tutor_reply and expected_answer:
        sim_val = compute_cosine(tutor_reply, expected_answer)
        sim_str = f"{sim_val * 100:.1f}%"
        try:
            import bert_score
            _, _, F1 = bert_score.score([tutor_reply.strip()], [expected_answer.strip()], model_type="distilbert-base-uncased", verbose=False)
            bert_str = f"{F1[0].item() * 100:.1f}%"
        except Exception:
            pass

    row_data = [
        now_str,
        question.strip(),
        tutor_reply.strip(),
        expected_answer,
        sim_str,
        bert_str,
        sources_str,
        lat_str,
        notes,
    ]

    # 1. Always append to CSV backup
    try:
        csv_exists = csv_path.exists()
        with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if not csv_exists:
                writer.writerow(HEADERS)
            writer.writerow(row_data)
    except Exception as e:
        print(f"[Logger] Warning writing CSV: {e}")

    # 2. Write to Excel (.xlsx) if openpyxl is available
    if not HAS_OPENPYXL:
        return

    try:
        if not xlsx_path.exists():
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Student Testing Log"
            ws.append(HEADERS)

            # Header row: clean, plain, no colors
            header_font = Font(name="Calibri", size=11, bold=True)
            for cell in ws[1]:
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

            ws.row_dimensions[1].height = 24
        else:
            wb = openpyxl.load_workbook(xlsx_path)
            ws = wb.active

        # Append data row
        ws.append(row_data)

        # Style data row: clean plain text, no fill colors
        row_idx = ws.max_row
        ws.row_dimensions[row_idx].height = 20
        cell_font = Font(name="Calibri", size=11)
        for col_idx, cell in enumerate(ws[row_idx], start=1):
            cell.font = cell_font
            if col_idx in (2, 3, 4):  # Question, Output, Expected
                cell.alignment = Alignment(vertical="center", wrap_text=True)
            else:
                cell.alignment = Alignment(horizontal="center", vertical="center")

        # Set sensible column widths
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
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = width

        wb.save(xlsx_path)
        print(f"[Auto-Log] Turn saved to Excel: {xlsx_path.name}")
    except PermissionError:
        print(f"[Auto-Log] Notice: {xlsx_path.name} is currently open in Excel. Appended to CSV backup instead.")
    except Exception as e:
        print(f"[Auto-Log] Notice: could not update .xlsx ({e}); saved to CSV backup.")
