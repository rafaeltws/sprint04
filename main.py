from machine import Pin
import time

energias = [8000, 5000, 2000]   
situacao = 0

nomes = ["EV1", "EV2", "EV3"]
bateria = [60, 35, 15]          
pedido = [2000, 2500, 3000]     
recebe = [0, 0, 0]              
estado = ["", "", ""]

potencia_minima = 1000


verde = [Pin(0, Pin.OUT), Pin(6, Pin.OUT), Pin(9, Pin.OUT)]
amarelo = [Pin(1, Pin.OUT), Pin(7, Pin.OUT), Pin(10, Pin.OUT)]
vermelho = [Pin(2, Pin.OUT), Pin(8, Pin.OUT), Pin(11, Pin.OUT)]


botao_troca = Pin(14, Pin.IN, Pin.PULL_UP)
botao_repr = Pin(15, Pin.IN, Pin.PULL_UP)



def gerenciar(energia):
    restante = energia


    ordem = [0, 1, 2]
    for i in range(3):
        for j in range(2):
            if bateria[ordem[j]] > bateria[ordem[j + 1]]:
                aux = ordem[j]
                ordem[j] = ordem[j + 1]
                ordem[j + 1] = aux

    for i in ordem:
        recebe[i] = 0
        if bateria[i] >= 100:
            estado[i] = "CHEIO"
        elif restante >= pedido[i]:
            recebe[i] = pedido[i]
            estado[i] = "ATIVA"
        elif restante >= potencia_minima:
            recebe[i] = restante
            estado[i] = "REDUZIDA"
        else:
            estado[i] = "ESPERA"
        restante = restante - recebe[i]

    return restante


def acender_leds():
    for i in range(3):
        verde[i].value(0)
        amarelo[i].value(0)
        vermelho[i].value(0)
        if estado[i] == "ATIVA":
            verde[i].value(1)
        elif estado[i] == "REDUZIDA":
            amarelo[i].value(1)
        elif estado[i] == "ESPERA":
            vermelho[i].value(1)


def carregar_baterias():
    for i in range(3):
        bateria[i] = bateria[i] + recebe[i] / 1000 * 1.5
        if bateria[i] > 100:
            bateria[i] = 100


def mostrar(energia, sobra):
    demanda = 0
    for i in range(3):
        if bateria[i] < 100:
            demanda = demanda + pedido[i]

    print("=========================================")
    print("Situacao", situacao + 1)
    print("Energia disponivel:", energia, "W")
    print("Demanda total:", demanda, "W")
    for i in range(3):
        print(nomes[i], "| bateria:", int(bateria[i]), "% | pede:", pedido[i],
              "W | recebe:", recebe[i], "W |", estado[i])

    if energia >= demanda:
        print("STATUS: RECARGA ATIVA")
    elif energia >= demanda / 2:
        print("STATUS: RECARGA CONTROLADA")
    else:
        print("STATUS: RECARGA LIMITADA")


def mostrar_representacao(energia):
    print("--- Representacao da energia disponivel ---")
    print("Decimal:", energia)
    print("Hexadecimal:", hex(energia))
    print("Binario:", bin(energia))


print("Estacao de recarga iniciada!")
mostrar_representacao(energias[situacao])

sobra = gerenciar(energias[situacao])
acender_leds()
mostrar(energias[situacao], sobra)

contador = 0
while True:
    if botao_troca.value() == 0:
        situacao = situacao + 1
        if situacao == 3:
            situacao = 0
        mostrar_representacao(energias[situacao])
        sobra = gerenciar(energias[situacao])
        acender_leds()
        mostrar(energias[situacao], sobra)
        time.sleep(0.3)  

    if botao_repr.value() == 0:
        mostrar_representacao(energias[situacao])
        time.sleep(0.3)

    contador = contador + 1
    if contador == 20:
        contador = 0
        carregar_baterias()
        sobra = gerenciar(energias[situacao])
        acender_leds()
        mostrar(energias[situacao], sobra)

    time.sleep(0.1)