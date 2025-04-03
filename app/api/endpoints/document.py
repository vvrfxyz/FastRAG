from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import document as models
from app.schemas import document as schemas
from app.services.pdf_service import PDFService
from app.services.embedding_service import EmbeddingService
from app.services.vector_db_service import VectorDBService

router = APIRouter()


@router.post("/upload/", response_model=schemas.Document)
async def upload_document(
        file: UploadFile = File(...),
        title: str = Form(None),
        db: Session = Depends(get_db)
):
    """上传文档并处理"""
    # 文件类型验证
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # 初始化服务
    pdf_service = PDFService()
    embedding_service = EmbeddingService()
    vector_db_service = VectorDBService()

    # 保存文件
    file_path = await pdf_service.save_upload(file)

    # 提取文本
    extraction_result = pdf_service.extract_text_with_fallback(file_path)
    full_text = ""
    if "text" in extraction_result:
        full_text = extraction_result["text"]
    elif "pages" in extraction_result:
        for page in extraction_result["pages"]:
            if isinstance(page, dict) and "text" in page:
                full_text += page["text"] + "\n"

    # 创建文档记录
    doc_title = title if title else file.filename
    db_document = models.Document(
        title=doc_title,
        file_path=str(file_path),
        content_type="pdf",
        content=full_text
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # 文本分块
    text_chunks = pdf_service.chunk_text(full_text)

    # 为每个块创建嵌入
    if text_chunks:
        embeddings = embedding_service.create_embeddings_by_chunks(text_chunks)

        # 准备元数据
        metadata_list = []
        for i, chunk in enumerate(text_chunks):
            metadata_list.append({
                "document_id": db_document.id,
                "chunk_index": i,
                "text": chunk,
                "title": doc_title
            })

        # 保存到向量数据库
        vector_ids = vector_db_service.add_embeddings(embeddings, metadata_list)

        # 创建嵌入记录
        for i, (chunk, vector_id) in enumerate(zip(text_chunks, vector_ids)):
            db_embedding = models.Embedding(
                document_id=db_document.id,
                text_chunk=chunk,
                chunk_index=i,
                vector_id=str(vector_id)
            )
            db.add(db_embedding)

        db.commit()

    return db_document


@router.get("/", response_model=List[schemas.Document])
def read_documents(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """获取所有文档"""
    documents = db.query(models.Document).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=schemas.Document)
def read_document(
        document_id: int,
        db: Session = Depends(get_db)
):
    """获取特定文档"""
    document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document