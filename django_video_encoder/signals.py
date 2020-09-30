from django.dispatch import Signal

sent_to_zencoder = Signal(providing_args=["instance", "result"])
sending_failed = Signal(providing_args=["instance", "error"])
encoding_failed = Signal(providing_args=["instance", "result"])
received_format = Signal(providing_args=["instance", "format", "result"])
