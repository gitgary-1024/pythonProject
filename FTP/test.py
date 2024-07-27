import alive_progress
import time

with alive_progress.alive_bar(100, bar='filling') as bar:
    for i in range(100):
        time.sleep(0.1)
        bar()
        bar.text('Processing item %d' % i)