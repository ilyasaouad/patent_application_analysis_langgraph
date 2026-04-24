import re
from typing import List, Dict, Optional

def decode_garbled_pdf_text(text: str) -> str:
    """
    Unified entry point for decoding text with font encoding issues.
    Specifically handles patent PDF artifacts like Caesar +29 shift.
    """
    if not text:
        return text
    
    detector = AutoEncodingDetector(verbose=False)
    if detector.is_text_garbled(text):
        # In a real scenario, we could try multiple decodings and pick the best.
        # But for now, we'll use the combined selector logic.
        return detector.fix_encoding(text)
    return text

class AutoEncodingDetector:
    """
    Ported from smart_extractor.py to handle patent PDF encoding issues.
    """
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # Common English words for quality checking
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'method', 'system', 'comprising', 'processing', 'data', 'neural',
            'network', 'artificial', 'intelligence', 'layer', 'output', 'input',
            'cancer', 'medical', 'images', 'patient', 'history', 'genetic'
        }

    def is_text_garbled(self, text: str) -> bool:
        """Determines if the text contains Caesar/Pattern-X artifacts."""
        # Check for control characters common in garbled PDFs
        if bool(re.search(r'[\x03\x0f\x1e]', text)):
            return True
        # Check for signature Caesar words (e.g., SURFHVVLQJ -> processing)
        if bool(re.search(r'\bSURFHVVLQJ\b|\bPHWKRG\b|\bV\\VWHP\b', text)):
            return True
        # Check for high ratio of long uppercase sequences with special PDF chars
        # [A-Z]{6,} with \, Þ, þ etc.
        if bool(re.search(r'[A-Z]{5,}.*[\\]', text)) or 'Þ' in text or 'þ' in text:
            return True
        return False

    def fix_encoding(self, text: str) -> str:
        """Applies selective decoding to fix the text."""
        # Selective Caesar Decode (Pattern 1 / +29 Shift)
        text = self._selective_caesar_decode(text)
        
        # Pattern 2 (-3 shift) - only if caret/underscore artifacts remain
        if any(c in text for c in '^_`$'):
            text = self._selective_pattern2_decode(text)
            
        return text

    def _selective_caesar_decode(self, text: str) -> str:
        """
        Decodes uppercase sequences that look like encoded words (6+ consecutive letters).
        Preserves normal patterns like [0001], section headers, and short acronyms.
        """
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            # Potential start of encoded sequence
            if char.isupper() or char in '\\[]':
                seq_start = i
                # Follow the sequence: letters, brackets, backslash, thorn, or control chars
                while i < len(text) and (
                    text[i].isupper() or 
                    text[i] in '\\[] Þþ' or 
                    ord(text[i]) in {0, 1, 2, 3, 15, 30}
                ):
                    i += 1
                
                sequence = text[seq_start:i]
                
                # Decision logic
                is_paragraph_num = (sequence.startswith('[') and any(c.isdigit() for c in sequence))
                
                # Check for line start (usually headers remain unencoded)
                prev_char = text[seq_start-1] if seq_start > 0 else '\n'
                is_line_start = prev_char in '\n\r'
                
                should_decode = False
                if is_paragraph_num:
                    should_decode = False
                elif is_line_start:
                    # Headers only decoded if they have explicit markers
                    should_decode = ('\\' in sequence or 'Þ' in sequence or 'þ' in sequence)
                else:
                    # Mid-text: check for long runs of uppercase
                    max_consecutive = 0
                    current_consecutive = 0
                    for c in sequence:
                        if c.isupper():
                            current_consecutive += 1
                            max_consecutive = max(max_consecutive, current_consecutive)
                        else:
                            current_consecutive = 0
                    
                    if max_consecutive >= 5 or '\\' in sequence or 'Þ' in sequence:
                        should_decode = True
                
                if should_decode:
                    decoded = []
                    for c in sequence:
                        code = ord(c)
                        if 65 <= code <= 90:  # A-Z -> lowercase +29
                            decoded.append(chr(code + 29))
                        elif code == 92:  # \ -> y
                            decoded.append('y')
                        elif code == 91:  # [ -> x
                            decoded.append('x')
                        elif code == 93:  # ] -> z
                            decoded.append('z')
                        elif code == 36:  # $ -> A
                            decoded.append('A')
                        elif c == 'Þ' or c == 'þ':
                            decoded.append('fi')
                        else:
                            decoded.append(c)
                    result.append(''.join(decoded))
                else:
                    result.append(sequence)
            else:
                result.append(char)
                i += 1
                
        # Post-process: clean up control characters and multiple spaces
        decoded_text = ''.join(result)
        decoded_text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', ' ', decoded_text)
        decoded_text = re.sub(r' +', ' ', decoded_text)
        return decoded_text

    def _selective_pattern2_decode(self, text: str) -> str:
        """Decodes words with ^, _, ` artifacts (+3 shift)."""
        def decode_chunk(match):
            word = match.group(0)
            # Only decode if it contains at least one special artifact character
            if not any(c in word for c in '^_`$'):
                return word
            
            decoded = []
            for char in word:
                code = ord(char)
                if code == 94: decoded.append('a')      # ^ -> a
                elif code == 95: decoded.append('b')    # _ -> b
                elif code == 96: decoded.append('c')    # ` -> c
                elif code == 36: decoded.append('A')    # $ -> A
                elif 97 <= code <= 122:                 # lowercase - 3
                    decoded.append(chr(((code - 97 - 3) % 26) + 97))
                elif 65 <= code <= 90:                  # uppercase - 3
                    decoded.append(chr(((code - 65 - 3) % 26) + 65))
                else:
                    decoded.append(char)
            return ''.join(decoded)

        # Apply to words containing special chars or long sequences
        return re.sub(r'\b[a-zA-Z\^\_\`\$]+\b', decode_chunk, text)
