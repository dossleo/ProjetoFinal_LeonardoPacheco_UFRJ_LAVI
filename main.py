from models.tratar_dados_brutos import GerarCSV
import os

os.system("cls")

ordem_inicial = 3
ordem_final = 10

GerarCSV(ordem_inicial,ordem_final).run()

