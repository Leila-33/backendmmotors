from pydantic import BaseModel, Field

class UploadRequest(BaseModel):
    filename: str = Field(..., description="Nom du fichier")
    content_type: str = Field(..., description="MIME type du fichier (ex: image/png)")