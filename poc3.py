from textractor import Textractor
extractor = Textractor(profile_name="poc")

from textractor.data.constants import TextractFeatures

document = extractor.analyze_document(
	file_source="poc_file.pdf",
	features=[TextractFeatures.TABLES]
)
# Saves the table in an excel document for further processing
document.tables[0].to_excel("output.xlsx")