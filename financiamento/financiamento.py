import pandas as pd
import numpy as np

pd.options.display.float_format = '{:.2f}'.format #opção para os floats aparecerem já com duas casas decimais

class Financiamento():
    def __init__(self, entrada: float, valor_total: float, prazo: int, taxa_juros: float, frequencia_anual=False, carencia=0, capitalizacao_juros=False, acrescimo_saldo=False): 
        """
        Estrutura básica do financiamento:
            valor_total (float): valor total do bem financiado.
            prazo (int): número de meses do financiamento.
            entrada (float): valor inicial pago.
            carencia (int): período de meses no qual não será realizado amortização.
            capitalizacao_juros (bool): valor dos juros é acréscido ao saldo devedor durante o período de carência e liquidado na primeira parcela.
            acrescimo_saldo (bool): valor da capitalização é acréscido ao saldo devedor e seu pagamento é
            taxa_juros (float): taxa de juros do financiamento, caso a taxa for anual, utilizar o parâmetro frequencia_anual como True.
        """
        self.valor_total = valor_total
        self.entrada = entrada
        self.prazo = prazo
        self.saldo_devedor = self.valor_total - self.entrada
        self.carencia = carencia
        self.capitalizacao_juros = capitalizacao_juros
        self.acrescimo_saldo = acrescimo_saldo
        
        if frequencia_anual:  #conversão dos juros caso for necessário para estar alinhado com a frequência dos prazos         
            self.taxa_juros = (1 + float(taxa_juros)) ** (1/12) - 1

        else:
            self.taxa_juros = taxa_juros
                
    def sac(self): 
        """
        Operação de financiamento pelo sistema de amortização constante.
            amortização: valor de pagamento do saldo devedor
            resultado: lista para armazenar as iterações do processo
            n_parcela: contador de parcelas iniciando em 0

        Além disso, possui rotinas especificas para algumas condições do financiamento, como carência, capitalização e acréscimo do juros capitalizado ao saldo.
        """
        self.amortizacao = self.saldo_devedor / self.prazo 
        resultado = [] 
        n_parcela = 0 
        resultado.append(
            {
                'Nº da parcela': n_parcela,
                'Saldo Devedor': self.saldo_devedor, 
                'Juros': 0,
                'Amortização': 0,
                'Valor Parcela': 0
            }
        ) #status inicial do financiamento salvo como um json básico

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
 
    def spc(self): 
        """
        Operação de financiamento pelo sistema de prestação constante - também conhecido sistema francês ou tabela price.
            fpv (fator de valor presente): denominador do cálculo da parcela no sistema Price.
            resultado: lista para armazenar as iterações do processo
            n_parcela: contador de parcelas iniciando em 0

        Além disso, possui rotinas especificas para algumas condições do financiamento, como carência, capitalização e acréscimo do juros capitalizado ao saldo, de forma análoga ao SAC.
        """
        self.fpv = (1 - (1 + self.taxa_juros) ** (- self.prazo)) / self.taxa_juros 
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
                        'Saldo Devedor': max(0, self.saldo_devedor),
                        'Amortização': self.amortizacao,
                        'Juros': juros,
                        'Valor Parcela': parcela
                    }
                )

            resultado = pd.json_normalize(resultado)
            return resultado
