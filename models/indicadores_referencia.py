import models
from models import get_raw_data, extrair_indicadores
import numpy as np
import os
import pandas as pd

class IndicadoresReferencia:
    def __init__(self,porcentagem_primeiros_sinais,no_ordens_frequencia,largura_banda,freq_passa_baixa,orden_filtro=5):
        self.porcentagem_primeiros_sinais = porcentagem_primeiros_sinais
        self.metricas_referencia = []

        self.freq_referencia = models.frequencias_rolamento
        self.largura_banda = largura_banda
        self.freq_passa_baixa = freq_passa_baixa
        self.ordem_filtro = orden_filtro
        self.no_ordens_frequencia = no_ordens_frequencia

    def ler_pasta(self,pasta):

        self.pasta = pasta
        self.lista_arquivos = os.listdir(self.pasta)

        slice = int(self.porcentagem_primeiros_sinais*len(self.lista_arquivos))

        return self.lista_arquivos[0:slice]

    def num_colunas(self,pasta):
        self.ler_pasta(pasta)

        Objeto_Leitura = get_raw_data.GetData(pasta,os.listdir(pasta)[0],0)
        vetor = np.array(Objeto_Leitura.dataset)

        return len(vetor[0,:])

    def extrair(self):

        for teste in range(len(models.PATH_TEST)):
            pasta = models.PATH_TEST[teste]
            self.df_pasta = []
            self.arquivos = self.ler_pasta(pasta)
            self.colunas = self.num_colunas(pasta)
            self.df_col = []

            for col in range(self.colunas):
                self.df_col = []
                for arquivo in self.arquivos:
                    sinal = get_raw_data.GetData(pasta,arquivo,col).Get()
                    Objeto_Extrair_Indicadores = extrair_indicadores.ExtrairIndicadores(sinal,
                                                                                        self.freq_referencia,
                                                                                        self.largura_banda,
                                                                                        self.freq_passa_baixa,
                                                                                        self.ordem_filtro)

                    dicionario = Objeto_Extrair_Indicadores.Get(self.no_ordens_frequencia)
                    self.df_col.append(dicionario)

                nome_json = f'teste{teste}_rolamento{col}'

                self.df = pd.json_normalize(self.df_col)
                self.df = pd.DataFrame(self.df)
                self.json_medio = self.df.mean()

                self.df_pasta.append({nome_json:self.json_medio})
            
            self.metricas_referencia.append(self.df_pasta)

            self.metricas_referencia = self.metricas_referencia[0:len(models.PATH_TEST)]

        return self.metricas_referencia




    def extrair_medias(self,no_teste,no_rolamento,indicador):

        dados = self.extrair()

        nome_teste = f'teste{no_teste}_rolamento{no_rolamento}'

        indicador_medio = dados[no_teste][no_rolamento][nome_teste][indicador]
        
        return indicador_medio