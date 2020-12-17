from hdfs import InsecureClient

client = InsecureClient("http://10.7.38.62:9870")
out = open('test.exe', 'wb')
client.list('exe/njrat')
with client.read('exe/njrat/asdgfasdfghiasdgfbuyaisdgvfiuasydgyfyiasgdfyi') as inp:
    out.write(inp.read())
    out.close()