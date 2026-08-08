import time
import threading

try:
    import pyamdgpuinfo
    HAS_AMD_SDK = True
except ImportError:
    HAS_AMD_SDK = False


class MonitorRadeonRX7600:
   
    def __init__(self, device_index=0, interval=0.1):
        self.device_index = device_index
        self.interval = interval
        self.running = False
        self._thread = None
        
        self.power_samples_watts = []
        self.gpu_utilization_samples = []
        self.vram_usage_samples_gb = []
        
        self.start_time = 0
        self.end_time = 0

    def start(self):
        """Inicia a coleta de métricas em segundo plano."""
        self.power_samples_watts = []
        self.gpu_utilization_samples = []
        self.vram_usage_samples_gb = []
        
        self.running = True
        self.start_time = time.perf_counter()
        
        self._thread = threading.Thread(target=self._monitor)
        self._thread.daemon = True
        self._thread.start()

    def _monitor(self):
        if HAS_AMD_SDK and pyamdgpuinfo.detect_gpus() > 0:
            gpu = pyamdgpuinfo.get_gpu(self.device_index)
            
            while self.running:
                try:
                    
                    power_w = gpu.query_power()
                    self.power_samples_watts.append(power_w)
                    
                    usage_pct = gpu.query_load() * 100.0
                    self.gpu_utilization_samples.append(usage_pct)

                    vram_bytes = gpu.query_vram_usage()
                    self.vram_usage_samples_gb.append(vram_bytes / (1024 ** 3))
                except Exception:
                    pass
                
                time.sleep(self.interval)
        else:
            print("[Aviso] Biblioteca 'pyamdgpuinfo' não encontrada. Instale com: pip install pyamdgpuinfo")
            while self.running:
                time.sleep(self.interval)

    def stop(self):
        """Para a amostragem e finaliza o cálculo."""
        self.running = False
        if self._thread:
            self._thread.join()
        self.end_time = time.perf_counter()

    @property
    def tempo_execucao_segundos(self):
        return max(0.0, self.end_time - self.start_time)

    @property
    def vram_pico_gb(self):
        if not self.vram_usage_samples_gb:
            return 0.0
        return max(self.vram_usage_samples_gb)

    @property
    def uso_medio_gpu_pct(self):
        if not self.gpu_utilization_samples:
            return 0.0
        return sum(self.gpu_utilization_samples) / len(self.gpu_utilization_samples)

    @property
    def potencia_media_watts(self):
        if not self.power_samples_watts:
            return 0.0
        return sum(self.power_samples_watts) / len(self.power_samples_watts)

    @property
    def energia_consumida_wh(self):
        horas = self.tempo_execucao_segundos / 3600.0
        return self.potencia_media_watts * horas

    @property
    def energia_consumida_kwh(self):
        return self.energia_consumida_wh / 1000.0

    def relatorio(self, tarifa_kwh=0.88):
        """Retorna um dicionário estruturado com todos os dados da GPU."""
        return {
            "placa_detectada": "XFX Radeon RX 7600 8GB",
            "tempo_execucao_s": round(self.tempo_execucao_segundos, 2),
            "vram_pico_gb": round(self.vram_pico_gb, 2),
            "uso_medio_gpu_pct": round(self.uso_medio_gpu_pct, 2),
            "potencia_media_watts": round(self.potencia_media_watts, 2),
            "energia_gasta_wh": round(self.energia_consumida_wh, 6),
            "energia_gasta_kwh": round(self.energia_consumida_kwh, 8),
            "custo_estimado_reais": round(self.energia_consumida_kwh * tarifa_kwh, 6)
        }

if __name__ == "__main__":
    monitor = MonitorRadeonRX7600(interval=0.1)
    
    print("Iniciando monitoramento da Radeon RX 7600...")
    monitor.start()

    print("Executando tarefa...")
    time.sleep(5) 
    monitor.stop()
    
    print("\n" + "=" * 45)
    print("   RELATÓRIO EXCLUSIVO DE CONSUMO DA GPU (AMD)   ")
    print("=" * 45)
    
    dados = monitor.relatorio(tarifa_kwh=0.88)
    for chave, valor in dados.items():
        print(f"{chave:<22}: {valor}")