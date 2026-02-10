import pdfplumber

print("Script started...")

pdf_path = "data/Law_pdf/Code_Travail_fr.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print("PDF opened successfully")
        print("Number of pages:", len(pdf.pages))

        full_text = ""

        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                full_text += text + "\n"

        print("Characters extracted:", len(full_text))
        print("\n--- SAMPLE TEXT ---\n")
        print(full_text[:10000000000])

except Exception as e:
    print("ERROR:", e)
