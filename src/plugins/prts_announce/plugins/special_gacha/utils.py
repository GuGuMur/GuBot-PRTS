def cleantext(text:str):
    lines = text.strip().split('\n')
    cleaned_lines = [line.strip() for line in lines]
    result = '\n'.join(cleaned_lines)
    return result