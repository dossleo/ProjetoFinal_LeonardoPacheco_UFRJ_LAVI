from models import _data_normalization, _frequency_features_extraction, _get_data, _low_pass_filter, _time_features_extraction, generate_rpm, get_rpm
import models
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Definição de frequência de aquisição
    fs = models.freq_sample
    
    # Gerar RPM
    gerar_rpm = generate_rpm.GenerateRPM(2000,20480)
    df_rpm = gerar_rpm.generate_array()
    # # gerar_rpm.plot_array()

    pegar_rpm = get_rpm.GetRPM(df_rpm,models.freq_sample)
    rpm_pontos = pegar_rpm.get_rpm_ponto_a_ponto()
    rpm_medio = pegar_rpm.get_rpm_medio()
    # # pegar_rpm.plot_picos()
    # # pegar_rpm.plot_rpm()

    # breakpoint()

for fault in range(len(models.fault_frequency)):
    # breakpoint()
# Passo 1: Descobrir maior frequência de defeito do rolamento
    maior_freq_defeito = max(models.fault_frequency)*rpm_medio
    dataframe = []
    for file in models.filenames:

    # Passo 2: Passar filtro passa baixa um pouco acima dessa frequência
        
        # Extraindo dados brutos
        raw_data = _get_data.GetData(models.path,file).Get()
        
        # Definindo ordem do filtro
        filter_order = 5

        # Definindo frequência de aplicação do filtro
        cutoff_filter = rpm_medio*2

        filtered_data = _low_pass_filter.LowPassFilter(raw_data,cutoff_filter,filter_order)
        # filtered_data.plot_time_domain(plot_raw_data = False)

        # Dados brutos após aplicação do filtro
        filtered_data = filtered_data.lowpass_filter()

        # breakpoint()

    # Passo 3: Normalizar os dados

        # Dados filtrados após aplicação da normalização da frequência
        normalized_data = _data_normalization.DataNormalized(filtered_data)
        # normalized_data.plot_normal_data()

        # breakpoint()

    # Passo 4: Aplicar métricas no domínio do tempo

        time_domain_data = _time_features_extraction.TimeFeatures(normalized_data.get())

    # Passo 5: Aplicar métricas no domínio da frequência

        frequency_domain_data = _frequency_features_extraction.FrequencyFeaturesExtraction(normalized_data.get(),rpm_medio)
        reference_frequency = models.fault_frequency[fault]*rpm_medio
        order_frequency = 9
        window_frequency = 50
        # frequency_domain_data.plot_frequency_domain(reference_frequency,order_frequency)
        # frequency_domain_data.plot_window(reference_frequency,window_frequency)
        # breakpoint()
        frequency_domain_data.window_around_frequency(reference_frequency,window_frequency)

    # Passo 6: Aplicar métricas do domínio do tempo nas window_frequencys de frequência
        orders_mean = frequency_domain_data.get_features(reference_frequency,window_frequency,order_frequency)
        metricas = frequency_domain_data.metricas

        dataframe.append(orders_mean)

        # print('-------------')
        # print('METRICAS')
        # print(metricas)
        # print('-------------')
        # print(orders_mean)
        # print('-------------')


    # Get RPM
    dataframe = pd.json_normalize(dataframe)
    print(dataframe)
    # breakpoint()
    # for feature in models.features:
    #     plt.plot(range(len(models.filenames)),dataframe[feature])
    #     plt.title(feature + "-" + str(models.fault_frequency[fault]))
    #     plt.show()

# breakpoint()