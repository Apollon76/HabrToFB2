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
	return page_content

def get_page_title(s):
	page_title = re.findall(r'<span class="post_title">.*?</span>', s)[0]
	page_title = page_title[len('<span class="post_title">'): -len('</span>')]
	return page_title

page_address = input('Введите URL:')
s = urlopen(page_address).read().decode()
page_title = get_page_title(s)
page_content = get_page_content(s)
images = re.findall(r'<img.*?>', page_content)
print(images)
images_names = list(map(lambda s: re.findall(r'src=".*?"', s)[0][len('src="') : -1], images))
images = []
for i in images_names:
	images += [str(base64.b64encode(urlopen(i).read()))[2 : -1]]
page_content = re.sub(r'<img src=".*?>', '<image l:href="#img' + chr(0) + '.jpg"/>', page_content)
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
for num, i in enumerate(page_content):
	page_content[num] = '<p>' + i + '</p>'
sys.stdout = open(page_title + '.fb2', 'w')
elements = ['<?xml version="1.0" encoding="utf-8"?>',
	'<FictionBook xmlns="http://www.gribuser.ru/xml/fictionbook/2.0" xmlns:l="http://www.w3.org/1999/xlink">',
	'	<description>',
	'		<title-info>',
	'			<book-title>' + page_title + '</book-title>',
	'		</title-info>',
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
