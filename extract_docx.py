import docx
import sys

def extract_docx_to_txt(docx_path, txt_path):
    try:
        doc = docx.Document(docx_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(full_text))
        print(f"Successfully extracted text to {txt_path}")
    except Exception as e:
        print(f"Error reading docx: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_docx.py <file_path>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "requirements_extracted.txt"
    extract_docx_to_txt(input_file, output_file)
