# simulador_financiamento
![Author](https://img.shields.io/badge/Author-Igor_Vallinote-blue)
![Python](https://img.shields.io/badge/Python-3%2B-yellow)
![License](https://img.shields.io/badge/License-MIT-red)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-green)

Código em Python para a construção de um simulador de financiamento no Sistema de Amortização Constante (SAC) e no Sistema de Prestação Constante (SPC ou Price).

O código deste repositório são baseados nas lógicas apresentadas no capítulo 12 do livro [Matemática Financeira e suas aplicações.](https://www.amazon.com.br/Matemática-Financeira-Aplicações-Alexandre-Assaf/dp/655977323X)
---
Tratam-se de duas classes, na qual a segunda herda os parâmetros iniciais da primeira, voltadas para duas operações:

1. Financiamento:
   Replica a operação de financiamento com base nos parâmetros básicos:
    - valor_total (float): valor total do bem financiado.
    - prazo (int): número de meses do financiamento.
    - entrada (float): valor inicial pago.
    - carencia (int): período de meses no qual não será realizado amortização.
    - capitalizacao_juros (bool): valor dos juros é acréscido ao saldo devedor durante o período de carência e liquidado na primeira parcela.
    - acrescimo_saldo (bool): valor da capitalização é acréscido ao saldo devedor e seu pagamento é 
    - taxa_juros (float): taxa de juros do financiamento, caso a taxa for anual, utilizar o parâmetro frequencia_anual como True.
  
   A partir disso, cabe ao usuário escolher dentre as duas modalidades de sistema de amortização disponível: a SAC ou SPC/Price.

2. Amortização:
   A ideia desta classe é estimar os impactos de amortizações extras e constantes no financiamento contratado para as duas modalidades consideradas aqui.
   Permitindo que as amortizações ocorram como desconto nos   valores futuros de parcelas, ou também no abatimento de parcelas futuras do financiamento.
