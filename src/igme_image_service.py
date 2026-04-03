"""
Helpers for fetching and caching IGME HTML pages and image assets for the viewer.
"""

import hashlib
import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from src.constants import IGME_HTML_CACHE_DIR, IGME_IMAGE_CACHE_DIR

ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
DEFAULT_IMAGE_CONTENT_TYPE = 'image/jpeg'


def _url_hash(value: str) -> str:
    """Return a stable cache key for a URL."""
    return hashlib.md5(value.encode()).hexdigest()


def _fetch_url_text(url: str, timeout: int = 10) -> str:
    """Fetch text content from a URL using the default viewer user agent."""
    request = urllib.request.Request(url, headers={'User-Agent': DEFAULT_USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode('utf-8')


def _fetch_url_bytes(url: str, timeout: int = 10) -> tuple[bytes, str]:
    """Fetch binary content and response content type from a URL."""
    request = urllib.request.Request(
        url,
        headers={
            'User-Agent': DEFAULT_USER_AGENT,
            'Referer': 'https://info.igme.es/',
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read(), response.headers.get('Content-Type', DEFAULT_IMAGE_CONTENT_TYPE)


def _normalize_igme_image_src(src: str) -> str:
    """Normalize a possibly-relative IGME image URL to an absolute URL."""
    if src.startswith('/'):
        return 'https://info.igme.es' + src
    if not src.startswith('http'):
        return 'https://info.igme.es/ielig/' + src
    return src


def extract_igme_images(html: str) -> List[Dict[str, str]]:
    """Extract image metadata from an IGME site page."""
    soup = BeautifulSoup(html, 'html.parser')
    images: List[Dict[str, str]] = []

    for img in soup.find_all('img'):
        src_attr = img.get('src')
        alt_attr = img.get('alt')
        src = src_attr if isinstance(src_attr, str) else ''
        alt = alt_attr if isinstance(alt_attr, str) else ''

        if not src:
            continue

        if any(skip in src.lower() for skip in ['icon', 'logo', 'banner', 'button']):
            continue

        normalized_src = _normalize_igme_image_src(src)
        if 'ielig' in normalized_src.lower() or 'fotos' in normalized_src.lower():
            images.append({
                'src': normalized_src,
                'alt': alt or 'Site image',
            })

    return images


def get_cached_igme_images(url: str) -> str:
    """Fetch and cache IGME page-derived image metadata, returning JSON text."""
    os.makedirs(IGME_HTML_CACHE_DIR, exist_ok=True)

    url_hash = _url_hash(url)
    html_cache_file = os.path.join(IGME_HTML_CACHE_DIR, f'{url_hash}.html')
    json_cache_file = os.path.join(IGME_HTML_CACHE_DIR, f'{url_hash}.json')

    if os.path.exists(json_cache_file):
        with open(json_cache_file, 'r', encoding='utf-8') as file:
            return file.read()

    if os.path.exists(html_cache_file):
        with open(html_cache_file, 'r', encoding='utf-8') as file:
            html = file.read()
    else:
        html = _fetch_url_text(url)
        with open(html_cache_file, 'w', encoding='utf-8') as file:
            file.write(html)

    json_response = json.dumps({'images': extract_igme_images(html)})
    with open(json_cache_file, 'w', encoding='utf-8') as file:
        file.write(json_response)

    return json_response


def get_cached_proxy_image(image_url: str) -> Dict[str, Any]:
    """Fetch and cache an IGME image asset for proxying."""
    os.makedirs(IGME_IMAGE_CACHE_DIR, exist_ok=True)

    url_hash = _url_hash(image_url)
    url_ext = os.path.splitext(urllib.parse.urlparse(image_url).path)[1].lower()
    if url_ext not in ALLOWED_IMAGE_EXTENSIONS:
        url_ext = '.jpg'

    cache_file = os.path.join(IGME_IMAGE_CACHE_DIR, f'{url_hash}{url_ext}')

    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as file:
            image_data = file.read()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
        }
        content_type = content_type_map.get(url_ext, DEFAULT_IMAGE_CONTENT_TYPE)
    else:
        image_data, content_type = _fetch_url_bytes(image_url)
        with open(cache_file, 'wb') as file:
            file.write(image_data)

    return {
        'content_type': content_type,
        'image_data': image_data,
    }

# Made with Bob