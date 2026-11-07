import shutil
import tempfile
import openpyxl
import subprocess

src = r"C:\Users\Vishesh G Devanur\OneDrive\Documents\student_testing_log.csv.xlsx"
tmp_path = r"D:\ENILS\enils\outputs\temp_user_log.xlsx"

# Copy even if open in Excel
cmd = f'powershell -Command "Copy-Item -Path \'{src}\' -Destination \'{tmp_path}\' -Force"'
subprocess.run(cmd, shell=True)

wb = openpyxl.load_workbook(tmp_path)
ws = wb.active
print(f"Total rows: {ws.max_row}, Total cols: {ws.max_column}")
for i in range(1, ws.max_row + 1):
    vals = [cell.value for cell in ws[i]]
    col1 = str(vals[1])[:35] if len(vals) > 1 and vals[1] is not None else ""
    col3 = str(vals[3])[:40] if len(vals) > 3 and vals[3] is not None else ""
    print(f"Row {i:2d}: Q={col1:35s} | Exp={col3}")
