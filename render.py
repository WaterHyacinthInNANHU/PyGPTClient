import json, os
import os.path as osp

from markdowngenerator import MarkdownGenerator


def fix_footnote(text):
	"""tranfer [^d^] to [^d]"""
	text = text.replace('^]', ']')
	return text


def get_filename(path):
	"""get filename from path"""
	filename = osp.basename(path).split('.')[:-1]
	filename = ''.join(filename)
	return filename


def read_one(result_path):
	with open(result_path) as f:
		data = json.load(f)
	text = data['details']['text']
	text = fix_footnote(text)
	text += '\n'
	card_body = data['details']['adaptiveCards'][0]['body']
	if len(card_body) < 2: # no reference
		refer = ''
	else:
		refer = card_body[-1]['text']
	filename = get_filename(result_path)
	return text, refer, filename


def write_item_to_md(doc, text, refer, filename):
	doc.addHeader(1, filename)
	doc.writeTextLine(text)
	doc.writeTextLine(f'{doc.addBoldedText(refer)}')


if __name__ == '__main__':
	results_dir = 'results'
	output_md_name = 'results.md'
	results_paths = [osp.join(results_dir, result) for result in sorted(os.listdir(results_dir))]

	with MarkdownGenerator(
		# By setting enable_write as False, content of the file is written
		# into buffer at first, instead of writing directly into the file
		# This enables for example the generation of table of contents
		filename=output_md_name, enable_write=False
	) as doc:
		# list all results in the directory
		for result_path in results_paths:
			text, refer, filename = read_one(result_path)
			write_item_to_md(doc, text, refer, filename)
