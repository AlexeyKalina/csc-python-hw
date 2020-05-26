class PreprocessingException(Exception):
    def __init__(self, message):
        self.message = message


class Preprocessor:
    def preprocess(self, program):
        lines = program.splitlines()
        result_lines = []
        for line in lines:
            without_comments = self.remove_comments(line)
            if without_comments != '' and not without_comments.isspace():
                clean_line = self.replace_spaces(without_comments)
                result_lines.append(clean_line)
        return '\n'.join(result_lines)

    def remove_comments(self, line):
        if '#' in line:
            return line.split('#')[0]
        return line

    def replace_spaces(self, line):
        prefix = 0
        space_count = 0
        for ch in line:
            if ch == ' ':
                space_count += 1
            elif ch == '\t':
                prefix += 1
            else:
                break
        if space_count % 4 != 0:
            raise PreprocessingException('wrong indentation')
        prefix += space_count // 4
        return '\t' * prefix + ' '.join(line.split())

