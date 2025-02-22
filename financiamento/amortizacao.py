import pandas as pd
import numpy as np
from financiamento.financiamento import Financiamento

pd.options.display.float_format = '{:.2f}'.format #opção para os floats aparecerem já com duas casas decimais

class Amortizacao(Financiamento):
    def __init__(self, financiamento, valor: float, sistema: str):
        """
        Usa os dados do financiamento existente para inicializar a classe pai.
        Acrescido à isso tem-se o valor mensal a ser adicionado à amortização e o respectivo sistema de financiamento.
        """
        super().__init__(
            entrada=financiamento.entrada,
            valor_total=financiamento.valor_total,
            prazo=financiamento.prazo,
            taxa_juros=financiamento.taxa_juros,
            carencia=financiamento.carencia,
            capitalizacao_juros=financiamento.capitalizacao_juros,
            acrescimo_saldo=financiamento.acrescimo_saldo
        )
        self.valor = valor
        self.sistema = sistema
    
    def amortizacao_parcela(self,dataframe):
        """
        Simulação do impacto de amortizações mensais fixas na opção de amortizar na parcela do financiamento. 
        Defini-se primeiro as colunas para os resultados da amortização extra fixa, juntamente com o novo intervalo a ser considerado no loop for, chamado aqui de 'inicio'
        """
        dataframe['Novo Saldo Devedor'] = np.nan
        dataframe['Nova Amortização'] = np.nan
        dataframe['Valor'] = np.nan
        dataframe['Novo Juros'] = np.nan
        dataframe['Nova Parcela'] = np.nan
        inicio = dataframe.loc[dataframe['Amortização'] > 0].reset_index(drop=True)['Nº da parcela'][0]
        contador = 0 

        if self.sistema == "SAC":
            for i in range(inicio, dataframe.shape[0]):
                if contador == 0:
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i, 'Saldo Devedor'] - self.valor 
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i, 'Juros'] 
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Amortização'] + dataframe.loc[i, 'Novo Juros'] + self.valor
                    contador += 1

                else:
                    dataframe.loc[i, 'Nova Amortização'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] / (self.prazo - dataframe.loc[i, 'Nº da parcela']) 
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i-1, 'Novo Saldo Devedor'] * self.taxa_juros
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Nova Amortização'] + dataframe.loc[i, 'Novo Juros'] + self.valor     
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] - (self.valor + dataframe.loc[i, 'Nova Amortização'])

                    if dataframe.loc[i, 'Novo Saldo Devedor'] < dataframe.loc[i, 'Nova Amortização']: #garantir que não hajam valores negativos, ou seja, o financiamento estimado foi quitado antes do prazo.
                        break
        
        else:
            for i in range(inicio, dataframe.shape[0]):
                if contador == 0:
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i, 'Saldo Devedor'] - self.valor 
                    dataframe.loc[i, 'Nova Amortização'] = dataframe.loc[i, 'Amortização']
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i, 'Juros'] 
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Valor Parcela']
                    contador += 1

                else:
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Valor Parcela']
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] * self.taxa_juros
                    dataframe.loc[i, 'Nova Amortização'] = dataframe.loc[i, 'Valor Parcela'] - dataframe.loc[i, 'Novo Juros']
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] - (self.valor + dataframe.loc[i, 'Nova Amortização'])
                    dataframe.loc[i, 'Valor'] = self.valor

                    if dataframe.loc[i, 'Novo Saldo Devedor'] < dataframe.loc[i, 'Nova Amortização']:
                        break
                        
        return dataframe.fillna(0)
        
    def amortizacao_prazo(self, dataframe):
        """
        Simulação do impacto de amortizações mensais fixas na opção de amortizar no do financiamento. 

        Ao contrário do método anterior, este visa verificar - dado a quantia de amortizações extras - o número equivalente de parcelas futuras a serem abatidas do financiamento.
        Este parâmetro é salvo na variável valor_abatido.
        """
        dataframe['Novo Saldo Devedor'] = np.nan
        dataframe['Valor'] = np.nan
        dataframe['Novo Juros'] = np.nan
        dataframe['Nova Parcela'] = np.nan
        inicio = dataframe.loc[dataframe['Amortização'] > 0].reset_index(drop=True)['Nº da parcela'][0]
        contador = 0
        valor_abatido = self.valor * self.prazo

        if self.sistema == "SAC":
            parcelas_abatidas = int(round(valor_abatido / dataframe['Amortização'].max(),0)) #cálculo das parcelas removidas para a tabela SAC
            fim = dataframe.shape[0] - parcelas_abatidas

            for i in range(inicio, fim):
                if contador == 0:
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i, 'Saldo Devedor'] - self.valor 
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i, 'Juros'] 
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Amortização'] + dataframe.loc[i, 'Novo Juros'] + self.valor
                    
                    contador += 1

                else:
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i-1, 'Novo Saldo Devedor'] * self.taxa_juros
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Amortização'] + dataframe.loc[i, 'Novo Juros'] + self.valor     
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] - (self.valor + dataframe.loc[i, 'Amortização'])
        
        else:
            #cálculo das parcelas removidas para a tabela Price
            dataframe['flag'] = dataframe.sort_values(by='Nº da parcela', ascending=False)['Amortização'].cumsum() >= (valor_abatido) 
            parcelas_abatidas = dataframe.shape[0] - dataframe.loc[dataframe['flag'] == True]['Nº da parcela'].max()
            fim = dataframe.shape[0] - parcelas_abatidas

            for i in range(inicio, fim):
                if contador == 0:
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i, 'Saldo Devedor'] - self.valor 
                    dataframe.loc[i, 'Nova Amortização'] = dataframe.loc[i, 'Amortização']
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i, 'Juros'] 
                    dataframe.loc[i, 'Valor'] = self.valor
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Valor Parcela']

                    contador += 1

                else:
                    dataframe.loc[i, 'Nova Parcela'] = dataframe.loc[i, 'Valor Parcela']
                    dataframe.loc[i, 'Novo Juros'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] * self.taxa_juros
                    dataframe.loc[i, 'Nova Amortização'] = dataframe.loc[i, 'Valor Parcela'] - dataframe.loc[i, 'Novo Juros']
                    dataframe.loc[i, 'Novo Saldo Devedor'] = dataframe.loc[i - 1, 'Novo Saldo Devedor'] - (self.valor + dataframe.loc[i, 'Nova Amortização'])
                    dataframe.loc[i, 'Valor'] = self.valor

        return dataframe.fillna(0)