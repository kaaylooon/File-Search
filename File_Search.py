import os 
import subprocess
import sys
import sqlite3
import inquirer
from inquirer import Text
import time
from yaspin import yaspin
import pyfiglet

f = pyfiglet.figlet_format("File Search", font="basic")

#===================================================
#chatgpt --> para .py e .exe, mete o path para o database paths.
#===================================================

if getattr(sys, 'frozen', False):  
	# Executando como .exe (PyInstaller)
	base_path = os.path.dirname(sys.executable)
else:  
	# Executando como .py
	base_path = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(base_path, "paths.db")

#===================================================

def criar_tabela():
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute('CREATE TABLE IF NOT EXISTS paths (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, path TEXT)')
	conn.commit() #altera a estrutura do banco dos dados, ent a conexão precisa chamar a commit, pra verificar a conexão ao disk
	conn.close()


def adicionar_PATH(titulo, path):
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute("INSERT INTO paths (titulo, path) VALUES (?, ?)", (titulo, path))
	conn.commit()
	conn.close()

def listar_PATHs():
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute("SELECT id, titulo, path FROM paths")
	paths = cur.fetchall()
	conn.close()
	return paths

def excluir_PATH(id_path):
	conn = sqlite3.connect(DB_NAME)
	cur = conn.cursor()
	cur.execute("DELETE FROM paths WHERE id = ?", (id_path,))
	conn.commit()
	conn.close()









def open_file(path):
	if os.name == 'nt':
		os.startfile(path)
	else:
		pass

def buscar(rootDir, keyword):
	resultados = []
	for relPath, dirs, files in os.walk(rootDir):
		for file in files:
			if(keyword.lower() in file.lower()):
				fullPath = os.path.join(relPath, file)
				resultados.append(fullPath)
	return resultados

def main():
	criar_tabela()

	while True:

		print(f'\n\n{  f}')

		resposta = inquirer.prompt([
			inquirer.List('choice', 
				message='Escolha', 
				choices=[
					'1. Buscar PDFs', 
					'2. Adicionar PATH', 
					'3. Remover PATH', 
					'4. Listar PATHs', 
					'5. Sair'
				],
				default='1. Buscar PDFs'),
		])

		choice = resposta['choice']

		if choice == '1. Buscar PDFs':
			paths = listar_PATHs()
			if not paths:
				print('Nenhum PATH cadastrado.')
				continue

			choices = [f'{id_path}. {titulo}' for id_path, titulo, path in paths]

			resposta_path = inquirer.prompt([
				inquirer.List(
					'path_choice',
					message='Selecione um PATH',
					choices=choices
				)
			])

			if not resposta_path:
				continue
			id_chose = int(resposta_path['path_choice'].split('.')[0])

			rootDir = next((path for id_path, titulo, path in paths if id_path == id_chose), None)

			if not rootDir:
				print('PATH inválido.')
				continue

			for id_path, titulo, path in paths:
				if id_path == id_chose:
					rootDir = path
					break

			if rootDir is None:
				print('PATH inválido.')
				continue

			key = [
			    Text('keyword', message="Palavra-chave"),
			]

			resposta = inquirer.prompt(key)
			keyword = resposta['keyword']

			with yaspin(text="Colors!") as sp:
			    # Support all basic termcolor text colors
			    colors = ("red", "green", "yellow", "blue", "magenta", "cyan", "white")

			    for color in colors:
			        sp.color, sp.text = color, 'Carregando...'
			        time.sleep(0.25)

			resultados = buscar(rootDir, keyword)

			if not resultados:
				print('Nenhum PDF encontrado...')
				continue

			arquivos_dict = {os.path.basename(p): p for p in resultados}

			arquivos_list = [f'{i}.  {filename}' for i, filename in enumerate(arquivos_dict.keys(), start=1)]

			resposta_pdf = inquirer.prompt([
				inquirer.List(
					'pdf_choice',
					message='Arquivos encontrados',
					choices=arquivos_list
				)
			])

			escolha_abre = int(resposta_pdf['pdf_choice'].split('.')[0])

			id_x = escolha_abre - 1

			if 0 <= id_x < len(arquivos_dict):
				confirm = inquirer.confirm("Isso vai abrir o arquivo selecionado."
                        " Continuar?", default=True)
				if confirm:
					open_file(resultados[id_x])
				else:
					pass
			else:
				print('Inválido.')
				continue

		elif choice == '2. Adicionar PATH':
			titulo = input('Título do PATH (Ex.:PDFs de física): ').strip()
			path = input('Diretório Completo (enter para usar o diretório do script): ').strip()
			if path == '':
				path = '.'
			if titulo and path:
				adicionar_PATH(titulo, path)
				print('Adicionado.')
			else:
				('Título e PATH são obrigatórios.')

		elif choice == '3. Remover PATH':
			id_path = input('ID do PATH: ')
			if id_path.isdigit():
				excluir_PATH(int(id_path))
				print('PATH removido.')
			else:
				print('ID inválido.')

		elif choice == '4. Listar PATHs':
			paths = listar_PATHs()
			if not paths:
				print('Nenhum PATH encontrado...')
			else:
				for id_path, titulo, path in paths:
					print(f'{id_path}\n{titulo}\n{path}')

		elif choice == '5. Sair':
			print('Saindo...')
			break
		else:
			print('Opção inválida.')

if __name__ == '__main__':
	main()