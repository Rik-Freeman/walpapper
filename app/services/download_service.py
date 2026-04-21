"""
Download service for Semantic Wallpaper application.
Handles downloading wallpapers from various sources (Picsum, Akspic).
"""

import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from PIL import Image


@dataclass
class DownloadResult:
    """Result of a wallpaper download operation."""
    success: bool
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    source: str = ""
    width: int = 0
    height: int = 0
    size_bytes: int = 0


class DownloadService:
    """Service for downloading wallpapers from external sources."""

    def __init__(self, cache_path: str, config_service=None):
        """
        Initialize download service.
        
        Args:
            cache_path: Directory to save downloaded wallpapers
            config_service: Optional ConfigService instance for configuration
        """
        self.cache_path = Path(cache_path)
        self.config_service = config_service
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "SemanticWallpaper/1.0"
        })

    def download_from_picsum(
        self,
        width: int = 1920,
        height: int = 1080,
        grayscale: bool = False,
        blur: bool = False
    ) -> DownloadResult:
        """
        Download a random wallpaper from Picsum Photos.
        
        Args:
            width: Desired image width
            height: Desired image height
            grayscale: If True, request grayscale image
            blur: If True, request blurred image
            
        Returns:
            DownloadResult with success status and file path
        """
        try:
            # Build URL
            base_url = "https://picsum.photos"
            params = {
                "width": width,
                "height": height,
            }
            if grayscale:
                params["grayscale"] = "true"
            if blur:
                params["blur"] = "true"

            # Add random seed to avoid caching
            seed = random.randint(1, 100000)
            url = f"{base_url}/seed/{seed}/{width}/{height}"

            # Download image
            response = self._session.get(url, timeout=30)
            response.raise_for_status()

            # Save to file
            return self._save_image(response.content, "picsum", width, height)

        except requests.RequestException as e:
            return DownloadResult(
                success=False,
                error_message=f"Picsum download failed: {str(e)}",
                source="picsum"
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                source="picsum"
            )

    def download_from_akspic(
        self,
        query: str = "nature",
        min_width: int = 1920,
        min_height: int = 1080,
        page: int = 1
    ) -> DownloadResult:
        """
        Download a wallpaper from akspic.ru.
        
        Args:
            query: Search query/category
            min_width: Minimum image width
            min_height: Minimum image height
            page: Page number for pagination
            
        Returns:
            DownloadResult with success status and file path
        """
        try:
            # Akspic search URL
            base_url = "https://akspic.ru/search/"
            params = {
                "q": query,
                "page": page,
            }

            # First, get the search results page
            response = self._session.get(
                base_url, 
                params=params, 
                timeout=30,
                headers={"Accept-Language": "en-US,en;q=0.9"}
            )
            response.raise_for_status()

            # Parse HTML to find image URLs (simplified - would need BeautifulSoup for full implementation)
            # For now, this is a placeholder structure
            # In production, you'd parse the HTML to extract actual image URLs
            
            # Placeholder: direct image URL construction (akspic structure)
            # This would need proper scraping logic
            image_url = self._extract_akspic_image_url(response.text, min_width, min_height)
            
            if not image_url:
                return DownloadResult(
                    success=False,
                    error_message="No suitable images found on Akspic",
                    source="akspic"
                )

            # Download the image
            img_response = self._session.get(image_url, timeout=30)
            img_response.raise_for_status()

            # Get dimensions from image
            from io import BytesIO
            img = Image.open(BytesIO(img_response.content))
            width, height = img.size

            return self._save_image(img_response.content, "akspic", width, height)

        except requests.RequestException as e:
            return DownloadResult(
                success=False,
                error_message=f"Akspic download failed: {str(e)}",
                source="akspic"
            )
        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}",
                source="akspic"
            )

    def _extract_akspic_image_url(self, html_content: str, min_width: int, min_height: int) -> Optional[str]:
        """
        Extract an image URL from Akspic HTML content.
        
        This is a simplified placeholder. In production, use BeautifulSoup.
        """
        # Placeholder implementation
        # Would need proper HTML parsing with BeautifulSoup
        return None

    def _save_image(
        self, 
        image_data: bytes, 
        source: str,
        width: int,
        height: int
    ) -> DownloadResult:
        """
        Save image data to file.
        
        Args:
            image_data: Raw image bytes
            source: Source name for filename
            width: Image width
            height: Image height
            
        Returns:
            DownloadResult with file path
        """
        try:
            # Ensure cache directory exists
            self.cache_path.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            import time
            timestamp = int(time.time())
            filename = f"{source}_{timestamp}_{width}x{height}.jpg"
            file_path = self.cache_path / filename

            # Validate and save image
            from io import BytesIO
            img = Image.open(BytesIO(image_data))
            
            # Convert to RGB if necessary (for JPEG saving)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            img.save(file_path, "JPEG", quality=95)

            # Get file size
            size_bytes = file_path.stat().st_size

            return DownloadResult(
                success=True,
                file_path=str(file_path),
                source=source,
                width=width,
                height=height,
                size_bytes=size_bytes
            )

        except Exception as e:
            return DownloadResult(
                success=False,
                error_message=f"Failed to save image: {str(e)}",
                source=source
            )

    def validate_resolution(
        self, 
        file_path: str, 
        min_width: int = 1920, 
        min_height: int = 1080
    ) -> Tuple[bool, int, int]:
        """
        Validate that an image meets minimum resolution requirements.
        
        Args:
            file_path: Path to image file
            min_width: Minimum required width
            min_height: Minimum required height
            
        Returns:
            Tuple of (is_valid, actual_width, actual_height)
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                is_valid = width >= min_width and height >= min_height
                return (is_valid, width, height)
        except Exception:
            return (False, 0, 0)

    def download_batch(
        self,
        count: int = 5,
        source: str = "picsum",
        categories: List[str] = None,
        min_width: int = 1920,
        min_height: int = 1080
    ) -> List[DownloadResult]:
        """
        Download multiple wallpapers.
        
        Args:
            count: Number of wallpapers to download
            source: Source to download from ('picsum' or 'akspic')
            categories: List of categories/queries (for akspic)
            min_width: Minimum image width
            min_height: Minimum image height
            
        Returns:
            List of DownloadResult objects
        """
        results = []
        
        if categories is None:
            categories = ["nature", "architecture", "abstract"]

        for i in range(count):
            if source == "picsum":
                # Randomize dimensions slightly for variety
                w = min_width + random.randint(0, 640)
                h = min_height + random.randint(0, 480)
                result = self.download_from_picsum(width=w, height=h)
            elif source == "akspic":
                # Cycle through categories
                category = categories[i % len(categories)]
                result = self.download_from_akspic(
                    query=category,
                    min_width=min_width,
                    min_height=min_height,
                    page=(i // len(categories)) + 1
                )
            else:
                result = DownloadResult(
                    success=False,
                    error_message=f"Unknown source: {source}"
                )

            results.append(result)

        return results

    def cleanup_cache(self, max_size_mb: int = 500) -> int:
        """
        Remove old files from cache if it exceeds maximum size.
        
        Args:
            max_size_mb: Maximum cache size in megabytes
            
        Returns:
            Number of files removed
        """
        if not self.cache_path.exists():
            return 0

        # Get all files sorted by modification time
        files = [
            (f, f.stat().st_mtime) 
            for f in self.cache_path.glob("*") 
            if f.is_file()
        ]
        files.sort(key=lambda x: x[1])

        # Calculate current size
        total_size = sum(f.stat().st_size for f, _ in files)
        max_size_bytes = max_size_mb * 1024 * 1024

        removed_count = 0
        
        # Remove oldest files until under limit
        while total_size > max_size_bytes and files:
            oldest_file, _ = files.pop(0)
            try:
                file_size = oldest_file.stat().st_size
                oldest_file.unlink()
                total_size -= file_size
                removed_count += 1
            except Exception:
                pass

        return removed_count
