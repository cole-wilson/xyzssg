import os
import re
import shutil
from markdown import markdown
import sass
import toml
from glob import glob
from jinja2 import Environment, PackageLoader, select_autoescape


builders = {
	"md": markdown
}


jinjenv = Environment(
	# loader=PackageLoader('.'),
	autoescape=select_autoescape(['html', 'xml'])
)

def getfiledata(file, parser=toml, sep="+++"):
	data = file.read().split('\n')
	if data[0] != sep:
		return {}, "\n".join(data)
	matter = body = ""
	scanning = True
	for line in data[1:]:
		if scanning:
			if line == sep:
				scanning = False
			else:
				matter += line + "\n"
		else:
			body += line + "\n"
	parsed = parser.loads(matter)
	parsed['file'] = file.name
	return parsed, body


data = toml.load('site.toml')

if os.path.isdir('_build'):
	shutil.rmtree('_build')

shutil.copytree(data['static']['dir'], '_build')

collections = {'all':[]}

# Move collection files and get data
for collection in data['collection']:
	pages = []
	if 'name' not in collection:
		collection['name'] = re.sub(r'[/\\\s\-_]', r'', collection['dir'])

	for filename in os.listdir(collection['dir']):
		# Open and read file data
		with open(os.path.join(collection['dir'], filename), 'r') as file:
			metadata, body = getfiledata(file)
		metadata['body'] = body
		# Add default parameters:
		for default in collection['defaults']:
			if default not in metadata:
				metadata[default] = collection['defaults'][default]
		if 'jinja' not in metadata:
			metadata['jinja'] = True	
		# get file endpath
		path = ""
		if 'path' in metadata:
			path = metadata['path']
		elif 'path' in collection:
			path = collection['path']
		else:
			path = collection['name']
		path = re.sub(r"[^/.a-zA-Z0-9-]", "", path.format(**metadata).replace(' ', '_')).lower()
		metadata['permalink'] = path
		# move file
		fpath = ''
		if path.split('.')[-1] in 'json html xml css js toml test csv'.split():
			fpath = os.path.join('_build', path.strip('/'))
		else:
			fpath = os.path.join('_build', path.strip('/'), 'index.html')
		fdir = os.path.join(*fpath.split(os.sep)[:-1])
		os.makedirs(fdir, exist_ok=True)
		with open(fpath, 'w+') as outfile:
			outfile.write(body)
		metadata['abs_path'] = os.path.abspath(fpath)
		pages.append(metadata)
	collections[collection['name']] = pages
	collections['all'] += pages

for file in collections['all']:
	if file['jinja']:
		template = jinjenv.get_template(file['abs_path'])
		template.render(the='variables', go='here')