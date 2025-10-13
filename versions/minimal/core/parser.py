import hcl2

class HCLParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse(self):
        with open(self.file_path, 'r') as f:
            return hcl2.load(f)