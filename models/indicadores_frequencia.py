import models
import numpy as np
import matplotlib.pyplot as plt
from models import filtro_passa_baixa, criar_pastas
import os


class DominioFrequencia():


    def __init__(self,sinal,rpm,freq_aquisicao = models.freq_aquisicao,path_to_save = f'{models.path_dados_tratados}/graficos_frequencia'):
        
        self.path_to_save = path_to_save

        self.sinal = sinal # dados brutos
        self.n_points_dado_bruto = len(self.sinal) # npoints
        self.rpm = rpm

        self.freq_aquisicao = freq_aquisicao

        self.frequencia_de_corte = 2000

        duracao_seg = self.n_points_dado_bruto/self.freq_aquisicao # duração em segundos

        self.dt = duracao_seg/self.freq_aquisicao # dt

    def run_fft(self,frequencia_de_corte = 0):

        frequencia_de_corte = frequencia_de_corte

        # Definindo o valor da amplitude de FFT
        self.fft_transform = np.fft.fft(self.sinal)
        self.fft_transform_conjugado = np.conj(self.fft_transform)

        self.fft_transform = np.abs(self.fft_transform*self.fft_transform_conjugado)

        self.fft_frequencia = np.fft.fftfreq(len(self.sinal),d=1/self.freq_aquisicao)

        primeiros_pontos = 1

        self.fft_transform[0:primeiros_pontos] = np.zeros(primeiros_pontos)

        if frequencia_de_corte == 0:
            self.fft_frequencia = self.fft_frequencia[0:len(self.fft_frequencia)//2]            
            self.fft_transform = self.fft_transform[0:len(self.fft_transform)//2]

        else:
            self.fft_frequencia = self.fft_frequencia[0:int(frequencia_de_corte)]
            self.fft_transform = self.fft_transform[0:int(frequencia_de_corte)]

        self.fft_frequencia = np.real(self.fft_frequencia)
        self.fft_transform = np.real(self.fft_transform)

    def plot_fft(self,freq_referencia=0,title='',salvar=True,plotar=True):
        self.run_fft(self.frequencia_de_corte)

        fig, ax = plt.subplots()
        ax.plot(np.abs(self.fft_frequencia),np.abs(self.fft_transform))
        if freq_referencia !=0:
            for i in range(10):
                plt.vlines(freq_referencia*(i+1),0,np.max(self.fft_transform),'red',linestyles='dotted')
        
        # Aumenta o tamanho da janela do plot para 10x10 polegadas
        fig.set_size_inches(12, 6)
        # print(np.max(self.fft_transform))
        plt.vlines(self.rpm,0,1.1*np.max(self.fft_transform),'green',linestyles='dotted')
        plt.ylim((0,100000))
        plt.xlim((0,self.frequencia_de_corte))

        plt.xlabel("Frequência [Hz]")
        plt.ylabel("Amplitude de Potência [W/Hz]")

        plt.gca().yaxis.get_major_formatter().set_powerlimits((0, 1))
        plt.tight_layout()
        
        plt.grid(axis='y')

        plt.title(f"Espectrograma {title}")

        if plotar:
            plt.show()

        if salvar:
            fig.savefig(f"{criar_pastas.create_dir(self.path_to_save)}/fft_freq_{np.round(freq_referencia,1)}Hz_Rotação_{np.round(self.rpm,1)}.png",dpi=600)
        
        plt.close()

    def banda_frequencia(self,freq_referencia:float,largura = 14,no_harmonicos=2):

        self.run_fft() 

        incerteza = 0.1
        
        harmonicos_frequencia = list()
        harmonicos_fourier = list()

        larg = largura*(1+incerteza)
        
        for harmonico in range(1,no_harmonicos+1):
            
            banda = np.logical_and(self.fft_frequencia >= (freq_referencia*(harmonico) - larg/2), self.fft_frequencia <= (freq_referencia*(harmonico) + larg/2))

            harmonicos_fourier.append(self.fft_transform[banda])
            harmonicos_frequencia.append(self.fft_frequencia[banda])

        return harmonicos_fourier, harmonicos_frequencia

    def plot_banda(self,freq_referencia:float,largura:float,title = '',salvar=True,plotar=True):

        lista_fourier_banda, lista_frequencia_banda = self.banda_frequencia(freq_referencia,largura)

        fig, ax = plt.subplots()
        fig.set_size_inches(14, 7)

        ax.plot(lista_frequencia_banda[0], lista_fourier_banda[0])

        # plt.ylim((0,1.1*np.max(self.fft_transform)))
        plt.ylim((0,100000))
        plt.xlim(freq_referencia-largura,freq_referencia+largura)

        plt.xlabel("Frequência [Hz]")
        plt.ylabel("Amplitude [mm/s²]")

        plt.gca().yaxis.get_major_formatter().set_powerlimits((0, 1))
        plt.tight_layout()

        plt.title(f"Banda de Frequência {title}")

        plt.vlines(freq_referencia,0,1.1*np.max(self.fft_transform),'green',linestyles='dotted')

        plt.grid(axis='y')

        if plotar:
            plt.show()

        if salvar:
            fig.savefig(f"{criar_pastas.create_dir(self.path_to_save)}/fft_banda_{np.round(freq_referencia,1)}Hz_Rotação_{np.round(self.rpm,1)}.png",dpi=600)
        
        plt.close()

    def pot_relativa_sinal(self,lista_sinal_fourier_banda,sinal_fourier_completo):
        pot_relativa = 0
        for i in range(len(lista_sinal_fourier_banda)):
            fourier_abs = np.sum(lista_sinal_fourier_banda[i])
            pot_relativa += fourier_abs/np.sum(sinal_fourier_completo[0:self.frequencia_de_corte])
        return pot_relativa

    def pot_sinal(self,lista_sinal_fourier_banda):
        pot = 0
        for i in range(len(lista_sinal_fourier_banda)):
            pot += np.sum(lista_sinal_fourier_banda[i])
        return pot
        