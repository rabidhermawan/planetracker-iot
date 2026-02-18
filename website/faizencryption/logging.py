from datetime import datetime, timezone
from flask import current_app
from pathlib import Path
import json
import mimetypes
import os

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

def _guess_mime(filename: str, data: bytes | None = None) -> str:
    mt, _ = mimetypes.guess_type(filename)
    return mt or 'application/octet-stream'

def _throughput_mb_s(num_bytes: int, seconds: float) -> float:
    if seconds <= 0:
        return float('inf')
    return num_bytes / (1024 * 1024) / seconds

def _write_log(entry: dict):
    log_path = current_app.config.get('CRYPTO_LOG_PATH')
    Path(os.path.dirname(log_path)).mkdir(parents=True, exist_ok=True)
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
def write_log(event:str, 
              filename:str,
              doc_uuid:str, 
              algorithm:str,
              plaintext_size,
              ciphertext_size,
              time_delta,
              iv_len=0,
              error=None
            ):
    if not error:
        _write_log({    
                'event': event,
                'result': 'ok',
                'timestamp': _now_iso(),
                'document_id': doc_uuid,
                'algorithm': algorithm,
                'filename': filename,
                'mime_type': _guess_mime(filename),
                'plaintext_size': plaintext_size,
                'ciphertext_size': ciphertext_size,  
                'iv_length': iv_len,
                'time_ms': round(time_delta * 1000, 3),
                'throughput_mb_s': round(_throughput_mb_s(plaintext_size, time_delta), 3),
        })
    else:
        _write_log({    
                'event': event,
                'result': 'error',
                'timestamp': _now_iso(),
                'algorithm': algorithm,
                'filename': filename,
                'mime_type': _guess_mime(filename),
                'plaintext_size': plaintext_size,
                'error' : str(error)
        })