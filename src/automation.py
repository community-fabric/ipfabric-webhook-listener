from models import Event



def process_event(event: Event):
    if event.type != 'snapshot' or event.action != 'discover' or event.status != 'completed':
        return
