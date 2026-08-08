import time
import threading
import pandas as pd
import psutil
from ollama import Client
from codecarbon import EmissionsTracker
from gpu_monitor import MonitorRadeonRX7600 

class ResourceMonitor:
    def __init__(self, interval=0.1):
        self.interval = interval
        self.running = False
        self.max_cpu = 0.0
        self.max_ram = 0.0
        self.initial_disk = None
        self.final_disk = None
        self._thread = None

    def start(self):
        self.running = True
        self.max_cpu = 0.0
        self.max_ram = 0.0
        self.initial_disk = psutil.disk_io_counters()
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()

    def _monitor(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=None)
                if cpu > self.max_cpu:
                    self.max_cpu = cpu

                ram_gb = psutil.virtual_memory().used / (1024 ** 3)
                if ram_gb > self.max_ram:
                    self.max_ram = ram_gb
            except Exception:
                pass
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        self.final_disk = psutil.disk_io_counters()

    @property
    def disk_read_mb(self):
        if self.initial_disk and self.final_disk:
            return (self.final_disk.read_bytes - self.initial_disk.read_bytes) / (1024 ** 2)
        return 0.0

    @property
    def disk_write_mb(self):
        if self.initial_disk and self.final_disk:
            return (self.final_disk.write_bytes - self.initial_disk.write_bytes) / (1024 ** 2)
        return 0.0

MODELO = "phi3.5" 

with open("perguntas.txt", "r", encoding="utf-8") as f:
    PERGUNTAS = [linha.strip() for linha in f if linha.strip()]

client = Client()

print("Preparando o ambiente (fase de aquecimento)...")
client.generate(model=MODELO, prompt="Oi")

print("Inicializando monitor de energia e monitor de hardware...")
tracker = EmissionsTracker(
    project_name=f"experimento_{MODELO.replace(':', '_')}",
    measure_power_secs=1,
    gpu_ids=[], 
    output_dir="."
)

hardware_monitor = ResourceMonitor()
gpu_monitor = MonitorRadeonRX7600(interval=0.1)  
tracker.start()
hardware_monitor.start()
gpu_monitor.start()                            

print(f"\nIniciando bateria de testes: Enviando {len(PERGUNTAS)} perguntas para o '{MODELO}'...")
print("Isso vai processar e gerar uma quantidade massiva de tokens. Aguarde...")

inicio_tempo = time.perf_counter()

total_tokens_gerados = 0
total_duracao_eval = 0.0
perguntas_respondidas = 0

try:
    for i, pergunta in enumerate(PERGUNTAS, start=1):
        resposta = client.generate(model=MODELO, prompt=pergunta)
        
        if 'eval_count' in resposta:
            total_tokens_gerados += resposta['eval_count']
            total_duracao_eval += resposta['eval_duration']
        
        perguntas_respondidas += 1
        if i % 10 == 0:
            print(f"Progresso: {i}/{len(PERGUNTAS)} perguntas processadas...")

    fim_tempo = time.perf_counter()
    tempo_total = fim_tempo - inicio_tempo

    tracker.stop()
    hardware_monitor.stop()
    gpu_monitor.stop()                          

    print("\n" + "=" * 40)
    print("        RESULTADOS DE DESEMPENHO        ")
    print("=" * 40)
    print(f"Modelo utilizado  : {MODELO}")
    print(f"Perguntas respondidas com sucesso  : {perguntas_respondidas}/{len(PERGUNTAS)}")
    print(f"Tempo total de processamento  : {tempo_total:.2f} segundos")
    print(f"Tempo médio por pergunta  : {tempo_total / perguntas_respondidas:.2f} segundos")

    if total_tokens_gerados > 0:
        velocidade_media = total_tokens_gerados / (total_duracao_eval / 1e9)
        print(f"Total de tokens gerados  : {total_tokens_gerados}")
        print(f"Velocidade média geral  : {velocidade_media:.2f} tokens/segundo")

    print("\n" + "=" * 40)
    print("      RECURSOS COMPUTACIONAIS    ")
    print("=" * 40)
    print(f"Pico de uso da CPU  : {hardware_monitor.max_cpu:.2f}%")
    print(f"Pico de memória RAM utilizada  : {hardware_monitor.max_ram:.2f} GB")
    print(f"Leitura em Disco durante o teste  : {hardware_monitor.disk_read_mb:.2f} MB")
    print(f"Escrita em Disco durante o teste  : {hardware_monitor.disk_write_mb:.2f} MB")    
    
    print("\n" + "=" * 40)
    print("           RESULTADOS ENERGÉTICOS         ")
    print("=" * 40)

    df = pd.read_csv("emissions.csv")
    ultimo_registro = df.iloc[-1]

    relatorio_gpu = gpu_monitor.relatorio()
    energia_gpu_wh = relatorio_gpu['energia_gasta_wh']
    energia_cpu_wh = ultimo_registro['cpu_energy'] * 1000
    
    consumo_total_wh = energia_cpu_wh + energia_gpu_wh

    print(f"Energia consumida pela CPU  : {energia_cpu_wh:.6f} Wh")
    print(f"Energia consumida pela GPU  : {energia_gpu_wh:.6f} Wh") 
    print(f"Consumo total de energia : {consumo_total_wh:.6f} Wh")
    print(f"Emissões de CO2 estimadas : {ultimo_registro['emissions'] * 1000:.6f} g de CO2")
    
    if total_tokens_gerados > 0:
        co2_por_mil_tokens = (ultimo_registro['emissions'] * 1000) / (total_tokens_gerados / 1000)
        print(f"Eficiência Carbônica  : {co2_por_mil_tokens:.6f} g de CO2 por 1k tokens")

    print("\n" + "=" * 40)
    print("      ESTIMATIVA FINANCEIRA ")
    print("=" * 40)

    TARIFA_KWH_PE = 0.88  
    
    consumo_kwh = consumo_total_wh / 1000.0
    custo_total_reais = consumo_kwh * TARIFA_KWH_PE

    print(f"Tarifa de Referência : R$ {TARIFA_KWH_PE:.2f} / kWh")
    print(f"Consumo Total em kWh : {consumo_kwh:.8f} kWh")
    print(f"Custo financeiro do teste : R$ {custo_total_reais:.8f}")

    if total_tokens_gerados > 0:
        custo_por_1k_tokens = (custo_total_reais / total_tokens_gerados) * 1000
        print(f"Custo por 1k tokens gerados : R$ {custo_por_1k_tokens:.8f}")

    print("\nOs dados detalhados foram salvos no arquivo 'emissions.csv'.")

except Exception as e:
    tracker.stop()
    hardware_monitor.stop()
    gpu_monitor.stop()
    print(f"\nOcorreu um erro durante o experimento: {e}")