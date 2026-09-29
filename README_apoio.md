# GoodWe Smart Charging Station

Estação de recarga inteligente de veículos elétricos, simulada no **Wokwi** com **Raspberry Pi Pico** e **MicroPython**. O projeto é inspirado no conceito do GoodWe Smart Energy Controller: um controlador que reparte uma quantidade limitada de energia entre vários veículos.

**Projeto da disciplina de Arquitetura de Computadores – Sprint 4**

**Integrantes:**
- Nome – RM
- Nome – RM
- Nome – RM

**Vídeo:** link do YouTube (não listado)
**Simulação no Wokwi:** link do projeto

---

## 1. Visão geral

A estação tem 3 veículos elétricos (EV1, EV2, EV3) conectados ao mesmo tempo. O Raspberry Pi Pico recebe a energia disponível, compara com a demanda dos veículos e decide quanto cada um recebe. O resultado aparece nos LEDs e no Monitor Serial.

| LED | Significado |
|---|---|
| 🟢 Verde | Recarga ativa (recebe a potência pedida) |
| 🟡 Amarelo | Recarga reduzida (recebe só parte do que pediu) |
| 🔴 Vermelho | Em espera (sem energia suficiente) |

---

## 2. Componentes e pinos

| Componente | Pinos do Pico |
|---|---|
| LEDs do EV1 (verde, amarelo, vermelho) | GP0, GP1, GP2 |
| LEDs do EV2 | GP6, GP7, GP8 |
| LEDs do EV3 | GP9, GP10, GP11 |
| Botão verde (troca a situação de energia) | GP14 |
| Botão azul (mostra decimal/hex/binário) | GP15 |
| Monitor Serial | USB / comunicação serial |

Cada LED usa um resistor de 330 Ω. Os botões usam o resistor interno de pull-up (`Pin.PULL_UP`), então ficam em 1 sem apertar e em 0 quando apertados.

---

## 3. Dados do sistema

| Veículo | Bateria inicial | Potência solicitada |
|---|---|---|
| EV1 | 60 % | 2.000 W |
| EV2 | 35 % | 2.500 W |
| EV3 | 15 % | 3.000 W |

Demanda total: **7.500 W**.

As três situações de energia disponível:

| Situação | Energia disponível |
|---|---|
| 1 – Alta disponibilidade | 8.000 W |
| 2 – Disponibilidade limitada | 5.000 W |
| 3 – Baixa disponibilidade | 2.000 W |

---

## 4. Como o algoritmo funciona

A estratégia é a **prioridade pela menor bateria**: quem está mais descarregado é atendido primeiro.

1. Os carros são colocados em ordem, da menor para a maior bateria (bubble sort).
2. Para cada carro, na ordem:
   - Se a energia restante for **maior ou igual ao pedido**, ele recebe tudo → **ATIVA** (verde).
   - Senão, se a energia restante for **pelo menos 1.000 W** (potência mínima), ele recebe o que sobrou → **REDUZIDA** (amarelo).
   - Senão, ele não recebe nada → **ESPERA** (vermelho).
   - Se a bateria já estiver em 100 %, o estado é **CHEIO** e ele não consome energia.
3. O que foi entregue é descontado da energia restante e o algoritmo passa para o próximo carro.

**Status geral da estação:**

| Condição | Status |
|---|---|
| Energia ≥ demanda total | RECARGA ATIVA |
| Energia ≥ metade da demanda | RECARGA CONTROLADA |
| Energia < metade da demanda | RECARGA LIMITADA |

**Simulação da carga:** a cada 2 segundos a bateria de cada carro aumenta de acordo com a potência que recebeu. Por isso a ordem de prioridade pode mudar durante a execução.

---

## 5. Resultados das três situações

Com as baterias iniciais (EV3 15 %, EV2 35 %, EV1 60 %):

| Situação | EV1 | EV2 | EV3 | Status |
|---|---|---|---|---|
| 1 – 8.000 W | 🟢 2.000 W | 🟢 2.500 W | 🟢 3.000 W | RECARGA ATIVA |
| 2 – 5.000 W | 🔴 0 W (espera) | 🟡 2.000 W (reduzida) | 🟢 3.000 W | RECARGA CONTROLADA |
| 3 – 2.000 W | 🔴 0 W (espera) | 🔴 0 W (espera) | 🟡 2.000 W (reduzida) | RECARGA LIMITADA |

**Por que a Situação 2 fica assim?** O EV3 tem a menor bateria e leva os 3.000 W que pediu. Sobram 2.000 W, que são menores que os 2.500 W do EV2, então ele fica reduzido com 2.000 W. Não sobra nada para o EV1, que espera.

**Por que a Situação 3 fica assim?** Só existem 2.000 W. O EV3 (menor bateria) recebe os 2.000 W, mesmo pedindo 3.000 W, e os outros dois ficam em espera.

---

## 6. Fluxo do sistema

```
        ENTRADAS
   - Energia disponível (botão)
   - Bateria de cada EV
   - Potência solicitada
              │
              ▼
     RASPBERRY PI PICO
   (MicroPython – processamento)
              │
              ▼
   Algoritmo de gerenciamento
         de energia
              │
     ┌────────┼────────┐
     ▼        ▼        ▼
    EV1      EV2      EV3
     │        │        │
     └────────┼────────┘
              ▼
      LEDs + Monitor Serial
```

**Perguntas que o professor pode fazer:**

| Pergunta | Resposta |
|---|---|
| Quais dados entram? | Energia disponível (escolhida pelo botão), bateria e potência solicitada de cada EV |
| Como o Pico processa? | A CPU executa o código MicroPython: compara valores, ordena e faz contas na função `gerenciar()` |
| Onde os dados ficam guardados? | Na RAM, nas listas `bateria`, `pedido`, `recebe` e `estado`. O código fica na memória flash |
| Como o sistema decide? | Pela prioridade da menor bateria, respeitando a energia restante e a potência mínima de 1.000 W |
| Quais saídas existem? | LEDs verde, amarelo e vermelho de cada EV e as informações no Monitor Serial |

---

## 7. Explicação do código (`main.py`)

| Parte do código | O que faz |
|---|---|
| Listas `energias`, `bateria`, `pedido`, `recebe`, `estado` | Guardam os dados da simulação na memória |
| `verde`, `amarelo`, `vermelho` | Listas com os pinos de saída (GPIO) dos LEDs |
| `botao_troca`, `botao_repr` | Pinos de entrada dos botões, com pull-up |
| `gerenciar(energia)` | Algoritmo principal: ordena por bateria e distribui a energia |
| `acender_leds()` | Liga o LED da cor certa conforme o estado de cada carro |
| `carregar_baterias()` | Aumenta a bateria de acordo com a potência recebida |
| `mostrar()` | Imprime no Serial a energia, a demanda, os dados dos EVs e o status |
| `mostrar_representacao()` | Imprime a energia em decimal, hexadecimal e binário |
| Laço `while True` | Lê os botões e, a cada 2 s, atualiza as baterias, o algoritmo e os LEDs |

---

## 8. Representação de dados

A energia disponível é um número inteiro, que o computador guarda em binário. Com o botão azul o programa mostra a mesma informação em três sistemas:

| Energia | Decimal | Hexadecimal | Binário |
|---|---|---|---|
| Situação 1 | 8000 | 0x1F40 | 1111101000000 |
| Situação 2 | 5000 | 0x1388 | 1001110001000 |
| Situação 3 | 2000 | 0x7D0 | 11111010000 |

**Conferindo 5000 em hexadecimal:** 1 × 4096 + 3 × 256 + 8 × 16 + 8 = 4096 + 768 + 128 + 8 = 5000.

**Por que o hexadecimal?** Cada dígito hexadecimal representa 4 bits, então ele é uma forma mais curta de escrever o binário: `0x1388` = `0001 0011 1000 1000`.

---

## 9. Arquitetura de Computadores no projeto

| Conceito | Aplicação no projeto |
|---|---|
| Processador | Microcontrolador RP2040 do Raspberry Pi Pico |
| Representação de dados | Inteiros para potência (W), valores decimais para bateria (%), textos para os estados |
| Sistemas numéricos | Decimal, hexadecimal e binário da energia disponível |
| Memória | RAM guarda os dados dos carros; flash guarda o programa |
| Entrada | Botões (GPIO) e dados simulados dos veículos |
| Processamento | Algoritmo de gerenciamento de energia |
| Saída | LEDs (GPIO) e Monitor Serial |
| Comunicação | Comunicação serial via USB |
| Automação | O sistema decide sozinho quem recarrega, quanto recebe e quem espera |

---

## 10. Relação com a GoodWe Smart Energy Controller

O GoodWe Smart Energy Controller gerencia o fluxo de energia de uma instalação (geração solar, rede e consumo) e ajusta a recarga do carro elétrico conforme a energia disponível.

| No projeto | No sistema real |
|---|---|
| Energia disponível (8.000 / 5.000 / 2.000 W) | Energia gerada pelo painel solar / limite da instalação |
| Pico com algoritmo | Controlador inteligente de energia |
| EV1, EV2, EV3 | Carregadores de veículos elétricos |
| LEDs verde, amarelo e vermelho | Indicação do estado de cada recarga |

O projeto é **educacional** e não reproduz todos os recursos de um produto comercial. Ele demonstra a ideia central: quando a energia é menor que a demanda, um algoritmo distribui o recurso de forma automática e eficiente.

---

## 11. Como executar

1. Abra o projeto no Wokwi (link no início deste documento).
2. Clique em **Play** para iniciar. O Monitor Serial mostra a Situação 1.
3. Aperte o **botão verde** para trocar entre as situações 1, 2 e 3.
4. Aperte o **botão azul** para ver a energia em decimal, hexadecimal e binário.

## 12. Arquivos do repositório

| Arquivo | Conteúdo |
|---|---|
| `main.py` | Código MicroPython |
| `diagram.json` | Circuito do Wokwi |
| `README.md` | Documentação do projeto |
