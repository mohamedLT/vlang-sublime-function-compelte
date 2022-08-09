from sys import float_repr_style
from typing import List
import sublime
import sublime_plugin
import glob
import os.path
import os
import pathlib
import subprocess
from dataclasses import dataclass

@dataclass
class const :
	name : str

@dataclass
class struct:
	methods :List
	vars:List[str]

@dataclass
class var:
	mame : str
	type : str

@dataclass
class function:
	name:str
	decl:str

@dataclass
class enum :
	name:str
	values:List[str]

@dataclass
class type:
	name:str


mods = {}
funcs=[]
files_mods = {}
def procces_docs(docs:str):
	lines = docs.splitlines()
	mod = lines[0].split(" ")[1] 
	mods[mod]={"consts" : [], "structs":[],"functions":[],"enums":[],"types":[]}
	i = 1
	while i<len(lines):
		line = lines[i]
		if not line.isspace()or len(line)>0 :
			if line.startswith("fn"):
				splited = line.split(" ")
				if splited[1][0]=='(':
					func_name =splited[4].split("(")[0] if splited[1]=="(mut" else  splited[3].split("(")[0]
				else :
					func_name = splited[1].split("(")[0]
				mods[mod]["functions"].append(function(func_name,line))
		i+=1
		get_all_func()			
			 
	
def get_all_func():
	global funcs
	funcs =[]
	for mod in mods.keys():
		for func in mods[mod]["functions"]:
			funcs.append(func)




class ExampleCommand(sublime_plugin.EventListener):
	def get_comp(self,view):
		if view.file_name() and view.file_name().split(".")[1]=="v":
			file_imports = []
			with open(view.file_name(),'r') as f:
				f.readline()
				f.readline()
				while True :
					line = f.readline()
					if len(line)==0:
						break
					if line.startswith("import"):
						file_imports.append(line.split(" ")[1].strip())




			new_path = pathlib.Path(os.path.split(view.file_name())[0])
			files_list = list(new_path.glob("**/*.v"))
			if len(files_list)>0:
				mods.clear()
				for mod in file_imports:
					res = subprocess.run(f"v doc -no-color {mod}",capture_output=True , text=True,shell=True)
					if res.stderr :
						splits = mod.split(".")
						path = new_path
						for split in splits: path/=split
						path = pathlib.Path(str(path)+".v")
						res = subprocess.run(f"v doc -no-color {path}",capture_output=True , text=True,shell=True)
					procces_docs(res.stdout)


	def on_post_save(self,view):
		self.get_comp(view)

	def on_activated_async(self,view):
		self.get_comp(view)
		


	def on_query_completions(self,view: sublime.View, prefix: str, locations:List):
		global funcs
		matches = []
		for func in funcs:
			if prefix in func.name:
				item = sublime.CompletionItem(func.name)
				item.annotation=func.decl
				matches.append(item)
		return matches






