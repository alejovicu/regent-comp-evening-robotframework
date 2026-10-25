"""Small wrapper around paramiko for reading catalog files from the SFTP server."""
import posixpath
import stat

import paramiko

from .config import settings


class SftpError(RuntimeError):
    pass


def _connect() -> tuple[paramiko.Transport, paramiko.SFTPClient]:
    try:
        transport = paramiko.Transport((settings.sftp_host, settings.sftp_port))
        transport.connect(username=settings.sftp_user, password=settings.sftp_password)
        return transport, paramiko.SFTPClient.from_transport(transport)
    except Exception as exc:
        raise SftpError(f"Cannot connect to SFTP server {settings.sftp_host}: {exc}")


def list_files() -> list[dict]:
    transport, sftp = _connect()
    try:
        entries = sftp.listdir_attr(settings.sftp_dir)
        return sorted(
            (
                {"filename": e.filename, "size": e.st_size, "modified": e.st_mtime}
                for e in entries
                if stat.S_ISREG(e.st_mode or 0) and not e.filename.startswith(".")
            ),
            key=lambda f: f["filename"],
        )
    except IOError as exc:
        raise SftpError(f"Cannot list '{settings.sftp_dir}': {exc}")
    finally:
        sftp.close()
        transport.close()


def read_file(filename: str) -> str:
    if "/" in filename or filename.startswith(".") or not filename:
        raise SftpError("Invalid file name")
    transport, sftp = _connect()
    try:
        with sftp.open(posixpath.join(settings.sftp_dir, filename), "r") as fh:
            return fh.read().decode("utf-8")
    except IOError:
        raise SftpError(f"File '{filename}' not found on SFTP server")
    except UnicodeDecodeError:
        raise SftpError(f"File '{filename}' is not valid UTF-8 text")
    finally:
        sftp.close()
        transport.close()
