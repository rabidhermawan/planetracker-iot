from src import scheduler
from src.plane_data import opensky_fetch_plane_data
from datetime import datetime

# def print_smth():
#   print(f"HELLO, I'm Emu Otori! {datetime.now()}")

scheduler.add_job(
    func=opensky_fetch_plane_data, 
    kwargs={"area":"SWISS"},
    trigger="interval",
    seconds=60,
    id="opsky_plane_fetch"
  )

# scheduler.add_job(
#     func=print_smth, 
#     trigger="interval",
#     seconds=5,
#     id="printsmth"
#   )
