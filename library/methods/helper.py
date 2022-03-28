import hashlib


class Helper:
    def hash_gen(self, str2hash: str) -> str:
        return hashlib.md5(str2hash.encode()).hexdigest()
