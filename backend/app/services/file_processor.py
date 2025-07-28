from fastapi import UploadFile
import pypdf
import markdown2
import io

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extracts raw text content from an uploaded file (PDF, TXT, or MD).
    
    Args:
        file (UploadFile): The file uploaded via the FastAPI endpoint.

    Returns:
        str: The extracted text content from the file.
        
    Raises:
        ValueError: If the file type is unsupported.
    """
    # Read the file content into a bytes buffer
    content = await file.read()
    file_stream = io.BytesIO(content)

    if file.filename.endswith(".pdf"):
        reader = pypdf.PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    
    elif file.filename.endswith(".txt"):
        return content.decode("utf-8")
        
    elif file.filename.endswith((".md", ".markdown")):
        html = markdown2.markdown(content.decode("utf-8"))
        # A simple way to strip HTML tags for this use case
        import re
        text = re.sub('<[^<]+?>', '', html)
        return text
        
    else:
        # Unsupported file type
        raise ValueError(f"Unsupported file type: {file.filename}")