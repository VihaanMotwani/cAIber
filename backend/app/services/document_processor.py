from typing import List
from pathlib import Path
from langchain.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


class DocumentProcessor:
    """Handles ingestion and processing of various document types."""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.docx', '.md'}
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def load_documents(self, directory_path: str) -> List[Document]:
        """Load all supported documents from a directory."""
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            print(f"Directory {directory_path} does not exist!")
            return documents
            
        for file_path in directory.rglob('*'):
            if file_path.suffix.lower() in self.supported_extensions:
                print(f"Processing: {file_path}")
                try:
                    docs = self._load_single_document(str(file_path))
                    documents.extend(docs)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        return documents
    
    def _load_single_document(self, file_path: str, original_name: str | None = None) -> List[Document]:
        file_path = Path(file_path)

        if file_path.suffix.lower() == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            loader = Docx2txtLoader(str(file_path))
        else:  # .txt, .md
            loader = TextLoader(str(file_path), encoding='utf-8')

        documents = loader.load()

        for doc in documents:
            doc.metadata['file_name'] = original_name or file_path.name
            doc.metadata['file_type'] = self._classify_document_type(
                original_name or file_path.name, doc.page_content
            )

        return self.text_splitter.split_documents(documents)
    
    def _classify_document_type(self, filename: str, content: str) -> str:
        """Classify document type based on filename and content."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # Business documents
        if any(term in filename_lower for term in ['strategy', 'business', 'plan', 'roadmap']):
            return 'business_strategy'
        
        # Security documents
        if any(term in filename_lower for term in ['incident', 'security', 'breach', 'vulnerability']):
            return 'security_incident'
        
        # Technical documents
        if any(term in filename_lower for term in ['architecture', 'network', 'infrastructure', 'system']):
            return 'technical_architecture'
        
        # Compliance documents
        if any(term in filename_lower for term in ['compliance', 'policy', 'gdpr', 'hipaa', 'audit']):
            return 'compliance'
        
        # Content-based classification
        if any(term in content_lower for term in ['incident response', 'security breach', 'attack']):
            return 'security_incident'
        elif any(term in content_lower for term in ['business objective', 'strategic initiative', 'expansion']):
            return 'business_strategy'
        
        return 'general'