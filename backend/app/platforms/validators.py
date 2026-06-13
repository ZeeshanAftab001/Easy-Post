# app/platforms/validators.py
from dataclasses import dataclass
from enum import Enum


class Platform(str, Enum):
    INSTAGRAM = "instagram"
    FACEBOOK  = "facebook"



@dataclass
class PlatformLimits:
    allowed_mime_types: list[str]
    max_size_bytes: int
    caption_max_length: int


LIMITS = {
    Platform.INSTAGRAM: PlatformLimits(["image/jpeg", "image/png"],                           8_388_608,  2200),
    Platform.FACEBOOK:  PlatformLimits(["image/jpeg", "image/png", "image/gif", "image/webp"], 10_485_760, 63206),
}


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]


def validate_for_platform(platform: Platform, image_bytes: bytes, mime_type: str, caption: str) -> ValidationResult:
    lim = LIMITS[platform]
    errors = []
    if mime_type not in lim.allowed_mime_types:
        errors.append(f"{platform.value} does not support {mime_type}. Allowed: {lim.allowed_mime_types}")
    if len(image_bytes) > lim.max_size_bytes:
        errors.append(f"Image too large for {platform.value}: {len(image_bytes)//1024}KB (max {lim.max_size_bytes//1024}KB)")
    if len(caption) > lim.caption_max_length:
        errors.append(f"Caption too long for {platform.value}: {len(caption)} chars (max {lim.caption_max_length})")
    return ValidationResult(valid=not errors, errors=errors)


def truncate_caption(caption: str, platform: Platform) -> str:
    limit = LIMITS[platform].caption_max_length
    return caption if len(caption) <= limit else caption[: limit - 3] + "..."