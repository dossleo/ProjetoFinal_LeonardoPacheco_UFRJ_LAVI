from msilib.schema import SelfReg
import matplotlib.pyplot as plt
import scipy.io
import numpy as np
import pandas as pd
import os
import glob
from math import sqrt
from scipy.fft import fft, fftfreq
import models
from models import _time_features_extraction

class FrequencyFeaturesExtraction():
    def __init__(self,data,rpm):
        
        self.data = data
        self.length = len(self.data)
        self.rpm = rpm

        t_final = self.length/models.freq_sample
        self.T = t_final/models.freq_sample
        self.time_vector = np.linspace(0.0, t_final, self.length, endpoint=False)
        self.ymin = -200
        self.ymax = 200

        self.features = models.features

    def RunFFT(self):
        self.fourier = fft(self.data)[0:self.length//2]
        primeiros_pontos = 2
        self.fourier[0:primeiros_pontos] = np.zeros(primeiros_pontos)
        self.freq = fftfreq(self.length,self.T)[0:self.length//2]
        
        self.fourier = np.real(self.fourier)
        self.freq = np.real(self.freq)
        self.freq = self.freq/self.rpm

    def PlotFrequencyDomain(self,freq_referencia,no_ordens = 1):

        self.RunFFT()

        plt.plot(self.freq, self.fourier)
        plt.title('Domínio da Frequência')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')

        for i in range(no_ordens):
            plt.vlines(freq_referencia*(i+1)/self.rpm,self.ymin,self.ymax,'red','dashed')

        plt.grid(True)
        plt.show()

    def JanelaFrequencia(self,freq_referencia,tamanho_janela_hz = 40):
        self.RunFFT()
        
        self.delta_f = (self.freq[-1]-self.freq[0])/len(self.freq)
        tamanho_janela_samples = int((tamanho_janela_hz/self.delta_f))

        elemento_referencia = int(freq_referencia/self.delta_f)

        inicio_janela = int(elemento_referencia-tamanho_janela_samples/2)
        fim_janela = int(elemento_referencia+tamanho_janela_samples/2)

        self.intervalo_janela = [inicio_janela,fim_janela]

        self.janela_freq = self.freq[inicio_janela:fim_janela]
        self.janela_fourier = self.fourier[inicio_janela:fim_janela]

        return self.janela_fourier

    def PlotJanela(self,freq_referencia,tamanho_janela_hz = 40):
        self.JanelaFrequencia(freq_referencia,tamanho_janela_hz)

        plt.plot(self.janela_freq,self.janela_fourier)
        plt.vlines(freq_referencia/self.rpm,self.ymin,self.ymax,'red','dashed')
        plt.ylim((self.ymin,self.ymax))
        plt.show()

    def MediaOrdens(self,freq_referencia,tamanho_janela_hz = 40,no_ordens = 1):
        metricas = []
        data_jason={}


        for i in range(no_ordens):
            dados = self.JanelaFrequencia(freq_referencia*(i+1),tamanho_janela_hz)
            metricas_frequencia = _time_features_extraction.TimeFeatures(dados)
            dicionario = metricas_frequencia.run()
            dicionario['ordem'] = i+1
            dicionario['frequencia_analisada'] = freq_referencia
            metricas.append(dicionario)

        self.metricas = pd.json_normalize(metricas)
        self.media = self.metricas.mean()

        for i in range(len(self.features)):
            data_jason[self.features[i]] = self.media[i]

        return data_jason
 
