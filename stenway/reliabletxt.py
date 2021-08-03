from enum import Enum


class ReliableTxtLines:
	def split(str):
		return str.split("\n")
	
	def join(lines):
		return "\n".join(lines)


class ReliableTxtEncoding(Enum):
	UTF_8 = 'utf-8'
	UTF_16 = 'utf-16-be'
	UTF_16_REVERSE = 'utf-16-le'
	UTF_32 = 'utf-32-be'


class ReliableTxtEncoder:
	def encode(str, encoding):
		encodingName = encoding.value
		return str.encode(encoding=encodingName)


class ReliableTxtDecoder:
	def getEncoding(bytes):
		if len(bytes) >= 3 and bytes[0] == 0xEF and bytes[1] == 0xBB and bytes[2] == 0xBF:
			return ReliableTxtEncoding.UTF_8;
		elif len(bytes) >= 2 and bytes[0] == 0xFE and bytes[1] == 0xFF:
			return ReliableTxtEncoding.UTF_16;
		elif len(bytes) >= 2 and bytes[0] == 0xFF and bytes[1] == 0xFE:
			return ReliableTxtEncoding.UTF_16_REVERSE;
		elif len(bytes) >= 4 and bytes[0] == 0 and bytes[1] == 0 and bytes[2] == 0xFE and bytes[3] == 0xFF:
			return ReliableTxtEncoding.UTF_32;
		raise Exception("Document does not have a ReliableTXT preamble")
	
	def decode(bytes):
		detectedEncoding = ReliableTxtDecoder.getEncoding(bytes)
		encodingName = detectedEncoding.value
		text = bytes.decode(encoding=encodingName)
		text = text[1:]
		return detectedEncoding, text


class ReliableTxtDocument:
	def __init__(self, text="", encoding=ReliableTxtEncoding.UTF_8):
		self._text = text
		self._encoding = encoding
	
	def setEncoding(self, encoding):
		self._encoding = encoding
		
	def setText(self, text):
		self._text = text
		
	def getEncoding(self):
		return self._encoding
		
	def getText(self):
		return self._text
		
	def getBytes(self):
		return ReliableTxtEncoder.encode(self._text, self._encoding)
	
	def getCodePoints(self):
		return StringUtil.getCodePoints(self._text)
		
	def setCodePoints(self, codePoints):
		self._text = StringUtil.fromCodePoints(codePoints)
	
	def save(self, filePath):
		encodingName = self._encoding.value
		
		file = open(filePath, 'w', encoding=encodingName, newline='\n')
		file.write('\ufeff')
		file.write(self._text)
		
	def load(filePath):
		bytes = None
		with open(filePath, "rb") as file:
			bytes = file.read()
		encoding, text = ReliableTxtDecoder.decode(bytes)
		return ReliableTxtDocument(text, encoding)


class StringUtil:
	def getCodePoints(str):
		return list(map(lambda c: ord(c), str))
	
	def fromCodePoints(codePoints):
		chars = list(map(lambda c: chr(c), codePoints))
		return "".join(chars)


class ReliableTxtCharIterator:
	def __init__(self, text):
		self._chars = StringUtil.getCodePoints(text)
		self._index = 0
	
	def getLineInfo(self):
		lineIndex = 0
		linePosition = 0
		for i in range(self._index):
			if (self._chars[i] == 0x0A):
				lineIndex += 1
				linePosition = 0
			else:
				linePosition += 1
		return lineIndex, linePosition
		
	def isEndOfText(self):
		return self._index >= len(self._chars)
	
	def isChar(self, c):
		if self.isEndOfText():
			return False
		return self._chars[self._index] == c
		
	def tryReadChar(self, c):
		if not self.isChar(c):
			return False
		self._index += 1
		return True
