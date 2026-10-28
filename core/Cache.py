import hashlib
import time
from pathlib import Path
from urllib.parse import urlparse
import requests
import shutil

class _CacheFolder:
    def __init__(self, Parent : str, FolderName : str, max_mb: float = 200, max_files: int = 2000,
                 min_interval: float = 0.5, session: requests.Session | None = None):
        self.folder = Path(f"{Parent}/{FolderName}")
        self.folder.mkdir(parents=True, exist_ok=True)
        self.max_bytes = int(max_mb * 1024 * 1024)
        self.max_files = max_files
        self.min_interval = min_interval  # secondes minimum entre deux requêtes
        self._last_request = 0.0
        self.session = session or requests.Session()

    def _path(self, url: str) -> Path:
        ext = Path(urlparse(url).path).suffix or ".bin"
        return self.folder / f"{hashlib.sha1(url.encode()).hexdigest()}{ext}"

    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def _evict(self):
        files = [f for f in self.folder.iterdir() if f.is_file() and f.suffix != ".tmp"]
        files.sort(key=lambda f: f.stat().st_mtime)  # les moins récemment utilisés d'abord
        total = sum(f.stat().st_size for f in files)
        while files and (total > self.max_bytes or len(files) > self.max_files):
            f = files.pop(0)
            total -= f.stat().st_size
            f.unlink(missing_ok=True)

    def get(self, url: str, throttle=True) -> Path:
        path = self._path(url)
        if path.exists():
            path.touch()
            return path

        if throttle:
            self._throttle()
        res = self.session.get(url, timeout=15)
        res.raise_for_status()
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(res.content)
        tmp.replace(path)
        self._evict()
        return path

    def drop(self):
        shutil.rmtree(self.folder, ignore_errors=True)
        self.folder.mkdir(parents=True, exist_ok=True)

class _CacheFile:
    def __init__(self, Name, default={}):
        self.Name = Name

    def Write(self):
        pass

    def Update(self):
        pass

    def Clear(self):
        pass

    def Default(self):
        pass

class Cache:
    def __init__(self):
        self.Cache = _CacheFolder(".", ".cache")
        self.Image = _CacheFolder(".cache", "image")

    def Drop(self):
        self.Cache.drop()
        self.Image.drop()
