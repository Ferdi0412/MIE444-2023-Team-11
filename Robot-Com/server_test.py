import robot

client = robot.get_client("Test", timeout=1000)

r = ord('\x00')
g = ord('\x33')
b = ord('\x66')

## print(b)

client.send(f'LED\n{r}\n{g}\n{b}'.encode('utf-8'))

client.send(b'CLAIM-OWNERSHIP')

client.send(b'MOVE-FORWARD\n10')

## client.send(b'LED-OFF')

print(client.recv())


print(client.recv())


print(client.recv())


print(client.recv())
