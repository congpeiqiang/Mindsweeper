#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/1/22 12:05
# @Author  : CongPeiQiang
# @File    : document.py
# @Software: PyCharm
import os
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.logger.logger import AppLogger

logger = AppLogger(name=os.path.basename(__file__), log_dir="logs", log_name="log.log").get_logger()

class InsertResponse(BaseModel):
    """Response model for document insertion operations

    Attributes:
        status: Status of the operation (success, duplicated, partial_success, failure)
        message: Detailed message describing the operation result
        track_id: Tracking ID for monitoring processing status
    """

    status: Literal["success", "duplicated", "partial_success", "failure"] = Field(
        description="Status of the operation"
    )
    message: str = Field(description="Message describing the operation result")
    track_id: str = Field(description="Tracking ID for monitoring processing status")
    code:int = Field(description="状态码", default=200)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "File 'document.pdf' uploaded successfully. Processing will continue in background.",
                "track_id": "upload_20250729_170612_abc123",
            }
        }