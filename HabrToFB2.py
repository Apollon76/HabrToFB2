import re, sys, base64
from urllib.request import *

def get_page_content(s):
	page_content = re.findall(r'<div class="content html_format">.*?<div class="clear"></div>', s, re.DOTALL)[0]
	page_content = page_content[len('<div class="content html_format">') : -len('<div class="clear"></div>')]
	page_content = re.sub(r'\n', '', page_content)
	page_content = re.sub(r'\t', '', page_content)
	page_content = re.sub(r'<br>', '\n', page_content)
	page_content = re.sub(r'<br/>', '\n', page_content)
	page_content = re.sub(r'<iframe.*?</iframe>', 'Здесь было видео!', page_content)
	page_content = re.sub(r'<b>', '<strong>', page_content)
	page_content = re.sub(r'</b>', '</strong>', page_content)
	return page_content

def get_page_title(s):
	page_title = re.findall(r'<span class="post_title">.*?</span>', s)[0]
	page_title = page_title[len('<span class="post_title">'): -len('</span>')]
	return page_title

def transliterate(string):
	capital_letters = {u'А': u'A',
					   u'Б': u'B',
					   u'В': u'V',
					   u'Г': u'G',
					   u'Д': u'D',
					   u'Е': u'E',
					   u'Ё': u'E',
					   u'Ж': u'Zh',
					   u'З': u'Z',
					   u'И': u'I',
					   u'Й': u'Y',
					   u'К': u'K',
					   u'Л': u'L',
					   u'М': u'M',
					   u'Н': u'N',
					   u'О': u'O',
					   u'П': u'P',
					   u'Р': u'R',
					   u'С': u'S',
					   u'Т': u'T',
					   u'У': u'U',
					   u'Ф': u'F',
					   u'Х': u'H',
					   u'Ц': u'Ts',
					   u'Ч': u'Ch',
					   u'Ш': u'Sh',
					   u'Щ': u'Sch',
					   u'Ъ': u'',
					   u'Ы': u'Y',
					   u'Ь': u'',
					   u'Э': u'E',
					   u'Ю': u'Yu',
					   u'Я': u'Ya'}
	lower_case_letters = {u'а': u'a',
					   u'б': u'b',
					   u'в': u'v',
					   u'г': u'g',
					   u'д': u'd',
					   u'е': u'e',
					   u'ё': u'e',
					   u'ж': u'zh',
					   u'з': u'z',
					   u'и': u'i',
					   u'й': u'y',
					   u'к': u'k',
					   u'л': u'l',
					   u'м': u'm',
					   u'н': u'n',
					   u'о': u'o',
					   u'п': u'p',
					   u'р': u'r',
					   u'с': u's',
					   u'т': u't',
					   u'у': u'u',
					   u'ф': u'f',
					   u'х': u'h',
					   u'ц': u'ts',
					   u'ч': u'ch',
					   u'ш': u'sh',
					   u'щ': u'sch',
					   u'ъ': u'',
					   u'ы': u'y',
					   u'ь': u'',
					   u'э': u'e',
					   u'ю': u'yu',
					   u'я': u'ya'}
	translit_string = ""
	for index, char in enumerate(string):
		if char in lower_case_letters.keys():
			char = lower_case_letters[char]
		elif char in capital_letters.keys():
			char = capital_letters[char]
			if len(string) > index+1:
				if string[index+1] not in lower_case_letters.keys():
					char = char.upper()
			else:
				char = char.upper()
		translit_string += char
	return translit_string

def get_file_name(s):
	letters = 'qwertyuiopasdfghjklzxcvbnmйцукенгшщзхъфывапролджэячсмитьбю'
	s = ''.join(list(map(lambda x: x if x.lower() in letters else ' ', s)))
	s = transliterate(s)
	return s

page_address = input('Введите URL:')
s = urlopen(page_address).read().decode()
#s = open('input.txt').read()
page_title = get_page_title(s)
file_name = get_file_name(page_title)
page_content = get_page_content(s)
images = re.findall(r'<img.*?>', page_content)
images_names = list(map(lambda s: re.findall(r'src=".*?"', s)[0][len('src="') : -1], images))
images = []
images_names = list(map(lambda s: s if s[:5] == 'http:' else 'http:' + s, images_names))
for i in images_names:
	images += [str(base64.b64encode(urlopen(i).read()))[2 : -1]]
page_content = re.sub(r'<img src=".*?>', '<image l:href="#img' + chr(0) + '.jpg"/>', page_content)
page_content = re.sub(r'<h[0-9]*?>', '<subtitle>', page_content)
page_content = re.sub(r'</h[0-9]*?>', '</subtitle>', page_content)
s1 = ''
q = 0
for i in page_content:
	if ord(i) == 0:
		s1 += str(q)
		q += 1
	else:
		s1 += i
page_content = s1
page_content = page_content.split('\n')
page_content = list(map(lambda s: '<p>' + s + '</p>', page_content))
sys.stdout = open(file_name + '.fb2', 'w')
elements = ['<?xml version="1.0" encoding="utf-8"?>',
	'<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">',
	'	<description>',
	'		<title-info>',
	'			<genre>article</genre>',
	'			<book-title>' + page_title + '</book-title>',
	'			<lang>ru</lang>',
	'		</title-info>',
	'		<document-info>',
	'			<src-url>' + page_address + '</src-url>',
	'		</document-info>',
	'	</description>',
	'<body>',
	'<title>',
	'<p>' + page_title + '</p>',
	'</title>',
	'<section>']
elements += page_content
elements += ['</section>',
	'</body>']
for num, i in enumerate(images):
	elements += ['<binary id="img' + str(num) + '.jpg" content-type="image/jpeg">' + i + '</binary>']
elements += ['</FictionBook>']
for i in elements:
	print(i)
