import PyU4V

conn = PyU4V.U4VConn(
    username='smc', password='smc', verify=False,
    array_id='000120200107', server_ip='10.40.223.200', port=8443
)

print(conn.common.get_uni_version())
