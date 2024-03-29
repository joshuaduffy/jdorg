from colorama import init
from invoke import Collection

from tasks import cf, client, monitoring

init()

# https://code.visualstudio.com/docs/python/debugging#_attach-to-a-local-script
# import ptvsd
# print("Waiting for debugger attach")
# ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
# ptvsd.wait_for_attach()
# breakpoint()

ns = Collection(cf, client, monitoring)
