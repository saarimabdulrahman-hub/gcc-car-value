import time

class OpenSooqStatistics:
    def __init__(self): self._s=0.0; self._e=0.0; self.p=0; self.f=0; self.r=0; self.x=0
    def start(self): self._s=time.time()
    def finish(self): self._e=time.time()
    def record_page(self): self.p+=1
    def record_found(self,n): self.f+=n
    def record_processed(self): self.r+=1
    def record_failure(self): self.x+=1
    @property
    def duration_ms(self): return (self._e-self._s)*1000 if self._e else 0.0
    def snapshot(self): return {"pages":self.p,"found":self.f,"processed":self.r,"failures":self.x,"duration_ms":self.duration_ms,"success_rate":(self.r/max(self.f,1))*100}
