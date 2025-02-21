import pandas as pd
import numpy as np

pd.options.display.float_format = '{:.2f}'.format #opção para os floats aparecerem já com duas casas decimais

class Financiamento():
    #estrutura básica do financiamento
    def __init__(self, bem_financiado, entrada, valor_total, prazo, taxa_juros, frequencia_anual=False, carencia=0, capitalizacao_juros=False, acrescimo_saldo=False): 
        self.valor_total = np.float64(valor_total)
        self.entrada = np.float64(entrada)
        self.bem_financiado = bem_financiado #categoria mais utilizada caso for construído um banco com as simulações
        self.prazo = int(prazo)
        self.saldo_devedor = self.valor_total - self.entrada
        self.carencia = carencia
        self.capitalizacao_juros = capitalizacao_juros
        self.acrescimo_saldo = acrescimo_saldo
        #conversão dos juros caso for necessário para estar alinhado com a frequência dos prazos
        if frequencia_anual:           
            self.taxa_juros = (1 + float(taxa_juros)) ** (1/12) - 1

        else:
            self.taxa_juros = taxa_juros
        
    #operação de financiamento pelo sistema de amortização constante.           
    def sac(self):
        self.amortizacao = self.saldo_devedor / self.prazo #valor de pagamento do saldo devedor

        resultado = [] #lista para armazenar as iterações do processo
        n_parcela = 0 #contador de parcelas
        #status inicial do financiamento salvo como um json básico
        resultado.append(
            {
                'Nº da parcela': n_parcela,
                'Saldo Devedor': self.saldo_devedor, 
                'Juros': 0,
                'Amortização': 0,
                'Valor Parcela': 0
            }
        )
        #estrutura de cáclulo para financiamentos com períodos de carência e captalização de juros com acréscimo do juros capitalizado ao saldo devedor
        if self.capitalizacao_juros and self.acrescimo_saldo and self.carencia > 0:

            for i in range(0, self.carencia):

                self.saldo_devedor = self.saldo_devedor * (1 + self.taxa_juros)             
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), # Evitar saldo devedor negativo
                        'Amortização': 0,
                        'Juros': 0,
                        'Valor Parcela': 0
                    }
                )

            self.amortizacao = self.saldo_devedor / self.prazo

            for i in range(0, self.prazo):

                juros = self.saldo_devedor * (self.taxa_juros)
                parcela = self.amortizacao + juros 
                self.saldo_devedor -= self.amortizacao
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor),  
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )
            resultado = pd.json_normalize(resultado)
            return resultado

        #estrutura de cáclulo para financiamentos com períodos de carência e captalização de juros, em que ao contrário da anterior, o juros não é acréscido ao saldo
        elif self.capitalizacao_juros and self.carencia > 0:
            saldo = self.saldo_devedor #necessidade de isolar o valor de referência do saldo devedor para a primeira parcela com juros capitalizado

            for i in range(0, self.carencia):

                saldo = saldo * (1 + self.taxa_juros) #nessa modalidade o juros incide direto sobre o saldo devedor         
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, saldo),  
                        'Amortização': 0,
                        'Juros': 0,
                        'Valor Parcela': 0
                    }
                )

            for i in range(0, self.prazo):

                if i == 0: #primeira parcela possui lógica distinta das demais
                    juros = (saldo * (1 + self.taxa_juros)) - self.saldo_devedor
                    parcela = self.amortizacao + juros 
                    self.saldo_devedor -= self.amortizacao
                    n_parcela += 1
                    resultado.append(
                        {
                            'Nº da parcela': n_parcela,
                            'Saldo Devedor': max(0, self.saldo_devedor), 
                            'Amortização': self.amortizacao,
                            'Juros': juros,
                            'Valor Parcela': parcela
                        }
                    )

                else:
                    juros = self.saldo_devedor * (self.taxa_juros)
                    parcela = self.amortizacao + juros 
                    self.saldo_devedor -= self.amortizacao

                    n_parcela += 1

                    resultado.append(
                        {
                            'Nº da parcela': n_parcela,
                            'Saldo Devedor': max(0, self.saldo_devedor),  
                            'Amortização': self.amortizacao,
                            'Juros': juros,
                            'Valor Parcela': parcela
                        }
                    )
            resultado = pd.json_normalize(resultado)
            return resultado
         
        #estrutura de cáclulo para financiamentos com períodos de carência
        elif self.carencia > 0:
            for i in range(0, self.carencia): #particulariedades do período de carência

                juros = self.saldo_devedor * self.taxa_juros #valor do juros
                n_parcela += 1 #acréscimo sequencial da parcela
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': self.saldo_devedor,
                        'Amortização': 0,
                        'Juros': juros,
                        'Valor Parcela': juros #durante a carência o valor dos juros é a parcela
                    }
                )

            for i in range(0, self.prazo): #cálculo padrão do financiamento

                juros = self.saldo_devedor * self.taxa_juros
                parcela = self.amortizacao + juros
                self.saldo_devedor -= self.amortizacao
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), 
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado) #dataframe gerado a partir do json construído nas iterações
            return resultado
    
        else: 
            for i in range(0, self.prazo):
                
                juros = self.saldo_devedor * (self.taxa_juros)
                parcela = self.amortizacao + juros 
                self.saldo_devedor -= self.amortizacao
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor),  
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado)
            return resultado
 
    #operação de financiamento pelo sistema de prestação constante - também conhecido sistema francês ou tabela price
    def spc(self): 
        self.fpv = (1 - (1 + self.taxa_juros) ** (- self.prazo)) / self.taxa_juros #fator valor presente para cálculo da parcela
        resultado = []
        n_parcela = 0
        resultado.append(
            {
                'Nº da parcela': n_parcela,
                'Saldo Devedor': max(0, self.saldo_devedor), 
                'Juros': 0,
                'Amortização': 0,
                'Valor Parcela': 0
            }
        )

        if self.capitalizacao_juros and self.carencia > 0:
            saldo = self.saldo_devedor

            for i in range(0, self.carencia):
                
                self.saldo_devedor = self.saldo_devedor * (1 + self.taxa_juros) 
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), 
                        'Amortização': 0,
                        'Juros': 0,
                        'Valor Parcela': 0    
                    }
                )

            parcela = self.saldo_devedor / self.fpv

            for i in range(0, self.prazo):

                juros = self.saldo_devedor * (self.taxa_juros)                    
                self.amortizacao = parcela - juros
                self.saldo_devedor -= self.amortizacao

                n_parcela += 1

                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), 
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado)
            return resultado

        elif self.carencia > 0:
            for i in range(0, self.carencia):

                juros = self.saldo_devedor * self.taxa_juros
                parcela = juros 
                n_parcela += 1
                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), 
                        'Amortização': 0,
                        'Juros': juros,
                        'Valor Parcela': parcela    
                    }
                )

            parcela = self.saldo_devedor / self.fpv

            for i in range(0, self.prazo):

                juros = self.saldo_devedor * (self.taxa_juros)                    
                self.amortizacao = parcela - juros
                self.saldo_devedor -= self.amortizacao

                n_parcela += 1

                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor), 
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado)
            return resultado
        
        else: 
            parcela = self.saldo_devedor / self.fpv

            for i in range(0, self.prazo):
                juros = self.saldo_devedor * self.taxa_juros                
                self.amortizacao = parcela - juros
                self.saldo_devedor -= self.amortizacao
                n_parcela += 1

                resultado.append(
                    {
                        'Nº da parcela': n_parcela,
                        'Saldo Devedor': max(0, self.saldo_devedor),  # Evitar saldo devedor negativo
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado)
            return resultado

class Amortizacao(Financiamento):
    def __init__(self, financiamento, valor, sistema):
        # Usa os dados do financiamento existente para inicializar a classe pai
        super().__init__(
            bem_financiado=financiamento.bem_financiado,
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
    # simulação do impacto de amortizações mensais fixas na opção de amortizar na parcela do financiamento. 
    def amortizacao_parcela(self,dataframe):
        #definição das colunas para os resultados da amortização extra fixa
        dataframe['Novo Saldo Devedor'] = np.nan
        dataframe['Nova Amortização'] = np.nan
        dataframe['Valor'] = np.nan
        dataframe['Novo Juros'] = np.nan
        dataframe['Nova Parcela'] = np.nan
        inicio = dataframe.loc[dataframe['Amortização'] > 0].reset_index(drop=True)['Nº da parcela'][0] #variável que garante que o cálculo incida apenas em períodos fora da carência.
        contador = 0 #ambos os sistemas possuem lógicas especificas para o primeiro mês.

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
    # simulação do impacto de amortizações mensais fixas na opção de amortizar no do financiamento. 
    def amortizacao_prazo(self, dataframe):
        dataframe['Novo Saldo Devedor'] = np.nan
        dataframe['Valor'] = np.nan
        dataframe['Novo Juros'] = np.nan
        dataframe['Nova Parcela'] = np.nan
        inicio = dataframe.loc[dataframe['Amortização'] > 0].reset_index(drop=True)['Nº da parcela'][0]
        contador = 0
        valor_abatido = self.valor * self.prazo #o modo como a amortização no prazo funciona, demanda o total a ser abatido do saldo devedor já ser levado em consideração

        if self.sistema == "SAC":
            parcelas_abatidas = int(round(valor_abatido / dataframe['Amortização'].max(),0)) #cálculo das parcelas removidas para a tabela SAC
            fim = dataframe.shape[0] - parcelas_abatidas #o loop for ocorre em um intervalo menor devido à remoção de parcelas futuras

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
            dataframe['flag'] = dataframe.sort_values(by='Nº da parcela', ascending=False)['Amortização'].cumsum() >= (valor_abatido) #cálculo das parcelas removidas para a tabela Price
            parcelas_abatidas = dataframe.shape[0] - dataframe.loc[spc['flag'] == True]['Nº da parcela'].max()
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