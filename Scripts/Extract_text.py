import pdfplumber

print("Starting PDF extraction...")

pdf_path = "Data/Law_pdf/Code_Travail_fr.pdf"

full_text = ""

with pdfplumber.open(pdf_path) as pdf:
    total_pages = len(pdf.pages)
    print(f"Total pages detected: {total_pages}")

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text()
        if text:
            full_text += text + "\n"

        
        print(f"Page {page_number}/{total_pages} extracted")

print("Extraction finished")
print("Total characters extracted:", len(full_text))

with open("data/full_law.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
