import sys
import traceback

class Tee:
    def __init__(self, filename):
        self.file = open(filename, 'w')
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_val, exc_tb, file=self)
        sys.stdout = self.stdout
        sys.stderr = self.stderr
        self.file.close()
        return False  # re-lève l'exception normalement

    def write(self, message):
        self.file.write(message)
        self.stdout.write(message)
        self.file.flush()

    def flush(self):
        self.file.flush()
        self.stdout.flush()
