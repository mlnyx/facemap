import PyPDF2

def extract_pdf_text(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'
    return text

if __name__ == '__main__':
    pdf_path = '000000076274_20251209071318.pdf'
    text = extract_pdf_text(pdf_path)
    with open('extracted_paper.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print('PDF 텍스트 추출 완료!')
