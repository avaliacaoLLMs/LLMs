import time
from ollama import Client
from gpu_monitor import MonitorRadeonRX7600 

MODELO = "phi3.5"
LIMITE_PERGUNTAS = None

with open("perguntas.txt", "r", encoding="utf-8") as f:
    PERGUNTAS = [linha.strip() for linha in f if linha.strip()]

if LIMITE_PERGUNTAS:
    PERGUNTAS = PERGUNTAS[:LIMITE_PERGUNTAS]

client = Client()

print("Preparando o ambiente (fase de aquecimento)...")
client.generate(model=MODELO, prompt="Oi")

gpu_monitor = MonitorRadeonRX7600(interval=0.1)

print(f"\nIniciando monitoramento da GPU para {len(PERGUNTAS)} pergunta(s)...")
gpu_monitor.start()

try:
    for i, pergunta in enumerate(PERGUNTAS, start=1):
        client.generate(model=MODELO, prompt=pergunta)
        print(f"Progresso: {i}/{len(PERGUNTAS)} pergunta(s) processada(s)...")

except Exception as e:
    print(f"\nOcorreu um erro durante o processamento: {e}")

finally:
    gpu_monitor.stop()

relatorio_gpu = gpu_monitor.relatorio()
energia_gpu_wh = relatorio_gpu['energia_gasta_wh']

print(f"\nEnergia consumida pela GPU : {energia_gpu_wh:.6f} Wh")