# %%
import rx.operators as op
from rx.subject import Subject

sender = Subject()
closer = Subject()

# Buffer should close whenever close() is called
events = sender

QUEUE = []


def dispatch(item):
    QUEUE.append(item)


def close():
    if QUEUE:
        items = [*QUEUE]
        QUEUE.clear()
        sender.on_next(items)


def process(buffer):
    print(buffer)
    for num in buffer:
        print(num)
        if num < 5:
            dispatch(num+5)
    close()


events.subscribe(process)
# %%

for i in range(3):
    dispatch(i)

close()


# %%
