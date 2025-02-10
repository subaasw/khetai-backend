from pathlib import Path
from fastapi import UploadFile, HTTPException
from typing import List

UPLOAD_DIRECTORY = Path("uploads")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

class FileUploader:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile) -> Path:
        file_path = self.upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return file_path

    async def save_files(self, files: List[UploadFile]) -> List[Path]:
        return [await self.save_file(file) for file in files]

class ImageUploader(FileUploader):
    async def save_file(self, file: UploadFile) -> Path:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid image file type.")
        return await super().save_file(file)

class AudioUploader(FileUploader):
    async def save_file(self, file: UploadFile) -> Path:
        if file.content_type not in ["audio/wav", "audio/mpeg"]:
            raise HTTPException(status_code=400, detail="Invalid audio file type.")
        return await super().save_file(file)