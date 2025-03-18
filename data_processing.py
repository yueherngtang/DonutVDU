import os
from pdf2image import convert_from_path

pdf_folder = "C:\\Users\\user\\OneDrive\\Documents\\MONASH SEM6\\FIT3164 - FYP\\data samples\\Alicia Assignment 2"
output_folder = "jpg_outputs2"
poppler_path = r"C:\\Users\\user\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"

# os.makedirs(output_folder, exist_ok=True)

# pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith('.pdf')]

# for pdf_file in pdf_files:
#     pdf_path = os.path.join(pdf_folder, pdf_file)
#     base_name = os.path.splitext(pdf_file[0])

#     print(f"Converting {pdf_file} to JPG...")

#     images = convert_from_path(pdf_path, dpi = 200, poppler_path= poppler_path)

#     for idx, image in enumerate(images):
#         output_path = os.path.join(output_folder,f"{base_name}_page_{idx+1}.jpg")

#         image.save(output_path, 'JPEG')
#         print(f"Saved: {output_path}")

# print("✅ All local PDFs converted to JPGs.")

jpg_files = [f for f in os.listdir(output_folder) if f.lower().endswith('.jpg')]


for i, filename in enumerate(jpg_files, start=80):
    new_name = f"{i:04}.jpg"  # Format: 001.jpg, 002.jpg, ...
    old_path = os.path.join(output_folder, filename)
    new_path = os.path.join(output_folder, new_name)

    os.rename(old_path, new_path)
    print(f"Renamed: {filename} -> {new_name}")