import collections
import os
import pickle


class Storage(object):
    def __init__(self, directory):
        self.directory = directory

    def _filename(self, name):
        if '/' in name:
            raise RuntimeError
        return os.path.join(self.directory, name)

    def _open(self, name, mode):
        basefilename = self._filename(name)
        file_data = open(basefilename + '.data', mode)
        file_meta = open(basefilename + '.meta', mode)
        return Item(file_data, file_meta)

    def create(self, name):
        return self._open(name, 'w+bx')

    def open(self, name):
        return self._open(name, 'rb')

    def openwrite(self, name):
        return self._open(name, 'r+b')

    def destroy(self, name):
        raise NotImplementedError


class Item(object):
    """
    Represents an open item.

    :ivar data: Open file-like object to data.
    """

    def __init__(self, file_data, file_meta):
        """
        :param file_data: Open file-like object to data file.
        :param file_meta: Open file-like object to meta file.
        """
        self.data = Data(file_data)
        self.meta = Meta(file_meta)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.data.close()
        self.meta.close()


class Data(object):
    """
    Data of item."
    """

    def __init__(self, file_data):
        self._file = file_data

    @property
    def size(self):
        self._file.seek(0, os.SEEK_END)
        return self._file.tell()

    def close(self):
        self._file.close()

    def read(self, offset, length):
        self._file.seek(offset)
        return self._file.read(length)

    def write(self, data, offset):
        self._file.seek(offset)
        return self._file.write(data)


class Meta(collections.MutableMapping):
    """
    Meta-data of item.
    """
    def __init__(self, file_meta):
        self._file = file_meta

        data = file_meta.read()
        if data:
            self._data = pickle.loads(data)
        else:
            self._data = {}

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def close(self):
        self._file.close()

    def flush(self):
        self._write()
        self._file.flush()

    def _write(self):
        self._file.seek(0)
        pickle.dump(self._data, self._file)
        self._file.seek(0)

