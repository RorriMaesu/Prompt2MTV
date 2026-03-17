import os
import urllib.request
import hashlib


class DownloadCancelledError(Exception):
    pass


def _parse_content_length(headers):
    raw_value = headers.get("Content-Length")
    if raw_value is None:
        return None
    try:
        parsed_value = int(raw_value)
    except (TypeError, ValueError):
        return None
    return parsed_value if parsed_value >= 0 else None


def probe_download_size(url, timeout=20):
    head_request = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(head_request, timeout=timeout) as response:
            content_length = _parse_content_length(response.headers)
            if content_length is not None:
                return content_length
    except Exception:
        pass

    range_request = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
    try:
        with urllib.request.urlopen(range_request, timeout=timeout) as response:
            content_range = response.headers.get("Content-Range", "")
            if "/" in content_range:
                tail_value = content_range.rsplit("/", 1)[-1].strip()
                try:
                    parsed_value = int(tail_value)
                except ValueError:
                    parsed_value = None
                if parsed_value is not None and parsed_value >= 0:
                    return parsed_value

            return _parse_content_length(response.headers)
    except Exception:
        return None


def download_file(url, dest_path, progress_callback=None, cancel_check=None, chunk_size=4 * 1024 * 1024, timeout=60):
    partial_path = f"{dest_path}.partial"
    existing_size = os.path.getsize(partial_path) if os.path.exists(partial_path) else 0
    request_headers = {}
    if existing_size > 0:
        request_headers["Range"] = f"bytes={existing_size}-"

    request = urllib.request.Request(url, headers=request_headers)

    with urllib.request.urlopen(request, timeout=timeout) as response:
        response_status = getattr(response, "status", None) or response.getcode()
        response_length = _parse_content_length(response.headers)
        is_resumed_download = existing_size > 0 and response_status == 206

        if existing_size > 0 and not is_resumed_download:
            existing_size = 0

        write_mode = "ab" if is_resumed_download else "wb"
        if write_mode == "wb" and os.path.exists(partial_path):
            os.remove(partial_path)

        total_bytes = existing_size + response_length if response_length is not None else None
        downloaded_bytes = existing_size

        if progress_callback:
            progress_callback(downloaded_bytes, total_bytes, is_resumed_download)

        with open(partial_path, write_mode) as output_file:
            while True:
                if cancel_check and cancel_check():
                    raise DownloadCancelledError(f"Download cancelled for {os.path.basename(dest_path)}")

                chunk = response.read(chunk_size)
                if not chunk:
                    break

                output_file.write(chunk)
                downloaded_bytes += len(chunk)

                if progress_callback:
                    progress_callback(downloaded_bytes, total_bytes, is_resumed_download)

    os.replace(partial_path, dest_path)
    return {
        "path": dest_path,
        "downloaded_bytes": downloaded_bytes,
        "total_bytes": total_bytes,
        "resumed": is_resumed_download,
    }


def calculate_sha256(file_path, chunk_size=4 * 1024 * 1024):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        while True:
            chunk = file_handle.read(chunk_size)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()