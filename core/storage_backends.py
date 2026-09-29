from django.conf import settings
from django.core.files.storage import FileSystemStorage, Storage
from django.utils.deconstruct import deconstructible

@deconstructible
class ConditionalRawMediaStorage(Storage):
    """Cloudinary raw-file storage in production; local media storage otherwise."""
    def _backend(self):
        if getattr(settings, "USE_CLOUDINARY", False):
            from cloudinary_storage.storage import RawMediaCloudinaryStorage
            return RawMediaCloudinaryStorage()
        return FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
    def _open(self, name, mode="rb"): return self._backend().open(name, mode)
    def _save(self, name, content): return self._backend().save(name, content)
    def delete(self, name): return self._backend().delete(name)
    def exists(self, name): return self._backend().exists(name)
    def listdir(self, path): return self._backend().listdir(path)
    def size(self, name): return self._backend().size(name)
    def url(self, name): return self._backend().url(name)
